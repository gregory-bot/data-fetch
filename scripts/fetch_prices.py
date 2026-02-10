"""
Fetch Current Prices from Binance
Retrieves 24hr ticker statistics and stores them in PostgreSQL
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance_client import BinanceClient
from database.connection import DatabaseConnection


def fetch_and_store_prices(symbols=None):
    """
    Fetch current prices from Binance and store in database
    
    Args:
        symbols (list): List of trading pairs to fetch (e.g., ['BTCUSDT', 'ETHUSDT'])
                       If None, fetches all symbols from .env or defaults
    """
    print("=" * 60)
    print("BINANCE PRICE FETCHER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize clients
    binance_client = BinanceClient()
    db = DatabaseConnection()
    
    # Default symbols if none provided
    if symbols is None:
        symbols_str = os.getenv('TRADING_PAIRS', 'BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,DOGEUSDT')
        symbols = [s.strip() for s in symbols_str.split(',')]
    
    print(f"Tracking {len(symbols)} symbols: {', '.join(symbols)}\n")
    
    try:
        # Connect to database
        db.connect()
        
        # Fetch data for each symbol
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            try:
                print(f"Fetching {symbol}...", end=" ")
                
                # Get 24hr ticker data from Binance
                ticker_data = binance_client.get_ticker_24hr(symbol)
                
                # Store in database
                db.insert_ticker_price(ticker_data)
                
                # Display info
                price = float(ticker_data['lastPrice'])
                change_pct = float(ticker_data['priceChangePercent'])
                volume = float(ticker_data['volume'])
                
                change_indicator = "📈" if change_pct > 0 else "📉"
                print(f"${price:,.2f} {change_indicator} {change_pct:+.2f}% | Vol: {volume:,.0f}")
                
                success_count += 1
                
            except Exception as e:
                print(f"✗ Failed: {e}")
                fail_count += 1
        
        print("\n" + "-" * 60)
        print(f"✓ Successfully stored: {success_count} symbols")
        if fail_count > 0:
            print(f"✗ Failed: {fail_count} symbols")
        print("-" * 60)
        
        # Show latest data from database
        print("\nLatest 5 records in database:")
        latest = db.get_latest_prices(5)
        
        for record in latest:
            symbol = record['symbol']
            price = float(record['price'])
            change_pct = float(record['price_change_percent']) if record['price_change_percent'] else 0
            timestamp = record['timestamp']
            
            print(f"  {symbol:10} ${price:10,.2f}  {change_pct:+6.2f}%  @{timestamp}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def fetch_all_prices():
    """Fetch prices for all available trading pairs (USDT pairs only)"""
    print("Fetching all USDT trading pairs...\n")
    
    binance_client = BinanceClient()
    
    try:
        # Get all ticker data
        all_tickers = binance_client.get_ticker_24hr()
        
        # Filter for USDT pairs only
        usdt_symbols = [
            ticker['symbol'] 
            for ticker in all_tickers 
            if ticker['symbol'].endswith('USDT')
        ]
        
        print(f"Found {len(usdt_symbols)} USDT trading pairs")
        print("Note: Fetching all pairs may take a while...\n")
        
        # Fetch and store (limit to top 20 by volume for demo)
        top_symbols = sorted(
            all_tickers, 
            key=lambda x: float(x['quoteVolume']), 
            reverse=True
        )[:20]
        
        symbols_to_fetch = [t['symbol'] for t in top_symbols if t['symbol'].endswith('USDT')]
        
        fetch_and_store_prices(symbols_to_fetch)
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch cryptocurrency prices from Binance')
    parser.add_argument(
        '--symbols', 
        type=str, 
        help='Comma-separated list of symbols (e.g., BTCUSDT,ETHUSDT)'
    )
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Fetch all USDT trading pairs (top 20 by volume)'
    )
    
    args = parser.parse_args()
    
    if args.all:
        fetch_all_prices()
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(',')]
        fetch_and_store_prices(symbols)
    else:
        # Use defaults from .env
        fetch_and_store_prices()
