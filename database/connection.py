"""
Database Connection Handler
Manages PostgreSQL database connections using psycopg2
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Handle PostgreSQL database connections"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'binance_data')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD')
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print(f"✓ Connected to database: {self.database}")
            return self.connection
        
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute a SQL query
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters
            fetch (bool): Whether to fetch results
            
        Returns:
            list: Query results if fetch=True, else None
        """
        try:
            if not self.connection:
                self.connect()
            
            self.cursor.execute(query, params)
            
            if fetch:
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return None
                
        except Exception as e:
            print(f"✗ Query execution failed: {e}")
            self.connection.rollback()
            raise
    
    def insert_ticker_price(self, ticker_data):
        """
        Insert ticker price data into database
        
        Args:
            ticker_data (dict): Ticker data from Binance API
        """
        query = """
        INSERT INTO ticker_prices (
            symbol, price, price_change, price_change_percent,
            weighted_avg_price, high_price, low_price, open_price,
            last_price, volume, quote_volume, bid_price, bid_qty,
            ask_price, ask_qty, num_trades, open_time, close_time
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        params = (
            ticker_data.get('symbol'),
            ticker_data.get('lastPrice'),
            ticker_data.get('priceChange'),
            ticker_data.get('priceChangePercent'),
            ticker_data.get('weightedAvgPrice'),
            ticker_data.get('highPrice'),
            ticker_data.get('lowPrice'),
            ticker_data.get('openPrice'),
            ticker_data.get('lastPrice'),
            ticker_data.get('volume'),
            ticker_data.get('quoteVolume'),
            ticker_data.get('bidPrice'),
            ticker_data.get('bidQty'),
            ticker_data.get('askPrice'),
            ticker_data.get('askQty'),
            ticker_data.get('count'),
            ticker_data.get('openTime'),
            ticker_data.get('closeTime')
        )
        
        self.execute_query(query, params, fetch=False)
    
    def insert_kline(self, symbol, interval, kline_data):
        """
        Insert kline (candlestick) data into database
        
        Args:
            symbol (str): Trading pair symbol
            interval (str): Time interval
            kline_data (list): Kline data from Binance API
        """
        query = """
        INSERT INTO klines (
            symbol, interval, open_time, open_price, high_price,
            low_price, close_price, volume, close_time,
            quote_asset_volume, num_trades, taker_buy_base_volume,
            taker_buy_quote_volume
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (symbol, interval, open_time) DO NOTHING
        """
        
        params = (
            symbol,
            interval,
            kline_data[0],  # Open time
            kline_data[1],  # Open
            kline_data[2],  # High
            kline_data[3],  # Low
            kline_data[4],  # Close
            kline_data[5],  # Volume
            kline_data[6],  # Close time
            kline_data[7],  # Quote asset volume
            kline_data[8],  # Number of trades
            kline_data[9],  # Taker buy base volume
            kline_data[10]  # Taker buy quote volume
        )
        
        self.execute_query(query, params, fetch=False)
    
    def get_latest_prices(self, limit=10):
        """Get latest prices from database"""
        query = """
        SELECT symbol, price, price_change_percent, 
               high_price, low_price, volume, timestamp
        FROM ticker_prices
        ORDER BY timestamp DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_symbol_history(self, symbol, limit=100):
        """Get price history for a specific symbol"""
        query = """
        SELECT price, price_change_percent, volume, timestamp
        FROM ticker_prices
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """
        return self.execute_query(query, (symbol, limit))


# Usage example
if __name__ == "__main__":
    # Test database connection
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Test query
        results = db.execute_query("SELECT COUNT(*) as count FROM ticker_prices")
        print(f"Total ticker prices in database: {results[0]['count']}")
        
        # Get latest prices
        latest = db.get_latest_prices(5)
        print("\nLatest 5 prices:")
        for row in latest:
            print(f"  {row['symbol']}: ${row['price']} ({row['price_change_percent']}%)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        db.close()
