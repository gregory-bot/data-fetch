"""
Fetch Historical Kline Data from Binance
Retrieves candlestick/kline data and stores in PostgreSQL
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance_client import BinanceClient
from database.connection import DatabaseConnection


def fetch_historical_klines(symbol, interval='1h', days=7):
    """
    Fetch historical kline data for a symbol
    
    Args:
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        interval (str): Kline interval (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
        days (int): Number of days of historical data to fetch
    """
    print("=" * 60)
    print("BINANCE HISTORICAL DATA FETCHER")
    print("=" * 60)
    print(f"Symbol: {symbol}")
    print(f"Interval: {interval}")
    print(f"Historical period: {days} days")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize clients
    binance_client = BinanceClient()
    db = DatabaseConnection()
    
    try:
        # Connect to database
        db.connect()
        
        # Calculate start time
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        print(f"Fetching klines from Binance API...\n")
        
        # Fetch klines
        klines = binance_client.get_klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        print(f"Retrieved {len(klines)} klines")
        print(f"Storing in database...\n")
        
        # Store each kline in database
        stored_count = 0
        for kline in klines:
            try:
                db.insert_kline(symbol, interval, kline)
                stored_count += 1
            except Exception as e:
                # Skip duplicates (handled by UNIQUE constraint)
                pass
        
        print(f"✓ Successfully stored {stored_count} new klines")
        
        # Display sample data
        if klines:
            print("\nSample of latest klines:")
            print(f"{'Time':<20} {'Open':>12} {'High':>12} {'Low':>12} {'Close':>12} {'Volume':>15}")
            print("-" * 85)
            
            for kline in klines[-5:]:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                volume = float(kline[5])
                
                print(f"{time_str:<20} {open_price:>12,.2f} {high_price:>12,.2f} {low_price:>12,.2f} {close_price:>12,.2f} {volume:>15,.2f}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def fetch_multiple_symbols(symbols, interval='1h', days=7):
    """Fetch historical data for multiple symbols"""
    print(f"\nFetching historical data for {len(symbols)} symbols...\n")
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}")
        print("-" * 60)
        
        try:
            fetch_historical_klines(symbol, interval, days)
        except Exception as e:
            print(f"✗ Failed to fetch {symbol}: {e}")
        
        # Add delay to avoid rate limiting
        if i < len(symbols):
            import time
            time.sleep(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch historical cryptocurrency data from Binance')
    parser.add_argument(
        '--symbol',
        type=str,
        default='BTCUSDT',
        help='Trading pair symbol (default: BTCUSDT)'
    )
    parser.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols to fetch'
    )
    parser.add_argument(
        '--interval',
        type=str,
        default='1h',
        choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'],
        help='Kline interval (default: 1h)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of historical data (default: 7)'
    )
    
    args = parser.parse_args()
    
    if args.symbols:
        # Multiple symbols
        symbols = [s.strip() for s in args.symbols.split(',')]
        fetch_multiple_symbols(symbols, args.interval, args.days)
    else:
        # Single symbol
        fetch_historical_klines(args.symbol, args.interval, args.days)
