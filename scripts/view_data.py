"""
View Data from PostgreSQL Database
Simple script to query and display stored cryptocurrency data
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import DatabaseConnection


def display_latest_prices(limit=20):
    """Display latest price data"""
    print("\n" + "=" * 80)
    print("LATEST CRYPTOCURRENCY PRICES")
    print("=" * 80)
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        results = db.get_latest_prices(limit)
        
        if not results:
            print("No data found in database.")
            return
        
        print(f"\nShowing latest {len(results)} price records:\n")
        print(f"{'Symbol':<12} {'Price':>14} {'Change %':>10} {'High 24h':>14} {'Low 24h':>14} {'Timestamp':<20}")
        print("-" * 94)
        
        for row in results:
            symbol = row['symbol']
            price = float(row['price'])
            change_pct = float(row['price_change_percent']) if row['price_change_percent'] else 0
            high_price = float(row['high_price']) if row['high_price'] else 0
            low_price = float(row['low_price']) if row['low_price'] else 0
            timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            change_indicator = "+" if change_pct > 0 else ""
            print(f"{symbol:<12} ${price:>13,.2f} {change_indicator}{change_pct:>9.2f}% ${high_price:>13,.2f} ${low_price:>13,.2f} {timestamp:<20}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        db.close()


def display_symbol_history(symbol, limit=50):
    """Display price history for a specific symbol"""
    print("\n" + "=" * 80)
    print(f"PRICE HISTORY FOR {symbol}")
    print("=" * 80)
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        results = db.get_symbol_history(symbol, limit)
        
        if not results:
            print(f"No data found for {symbol}.")
            return
        
        print(f"\nShowing last {len(results)} records:\n")
        print(f"{'Price':>14} {'Change %':>10} {'Volume':>18} {'Timestamp':<20}")
        print("-" * 64)
        
        for row in results:
            price = float(row['price'])
            change_pct = float(row['price_change_percent']) if row['price_change_percent'] else 0
            volume = float(row['volume']) if row['volume'] else 0
            timestamp = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            change_indicator = "+" if change_pct > 0 else ""
            print(f"${price:>13,.2f} {change_indicator}{change_pct:>9.2f}% {volume:>18,.2f} {timestamp:<20}")
        
        # Calculate statistics
        if len(results) > 1:
            prices = [float(r['price']) for r in results]
            max_price = max(prices)
            min_price = min(prices)
            avg_price = sum(prices) / len(prices)
            
            print("\n" + "-" * 64)
            print(f"Statistics (last {len(results)} records):")
            print(f"  Highest: ${max_price:,.2f}")
            print(f"  Lowest:  ${min_price:,.2f}")
            print(f"  Average: ${avg_price:,.2f}")
            print(f"  Range:   ${max_price - min_price:,.2f} ({((max_price - min_price) / min_price * 100):.2f}%)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        db.close()


def display_database_stats():
    """Display overall database statistics"""
    print("\n" + "=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    
    db = DatabaseConnection()
    
    try:
        db.connect()
        
        # Count ticker prices
        ticker_count = db.execute_query("SELECT COUNT(*) as count FROM ticker_prices")[0]['count']
        
        # Count klines
        kline_count = db.execute_query("SELECT COUNT(*) as count FROM klines")[0]['count']
        
        # Count unique symbols in ticker_prices
        symbols_query = """
            SELECT symbol, COUNT(*) as record_count, 
                   MAX(timestamp) as last_update
            FROM ticker_prices
            GROUP BY symbol
            ORDER BY record_count DESC
        """
        symbols = db.execute_query(symbols_query)
        
        print(f"\nTotal Records:")
        print(f"  Ticker Prices: {ticker_count:,}")
        print(f"  Klines:        {kline_count:,}")
        
        if symbols:
            print(f"\nTracked Symbols ({len(symbols)}):")
            print(f"{'Symbol':<12} {'Records':>10} {'Last Update':<20}")
            print("-" * 44)
            
            for row in symbols[:15]:  # Show top 15
                symbol = row['symbol']
                count = row['record_count']
                last_update = row['last_update'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{symbol:<12} {count:>10,} {last_update:<20}")
            
            if len(symbols) > 15:
                print(f"\n... and {len(symbols) - 15} more symbols")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        db.close()


def interactive_menu():
    """Interactive menu for data viewing"""
    while True:
        print("\n" + "=" * 80)
        print("BINANCE DATA VIEWER")
        print("=" * 80)
        print("\nOptions:")
        print("  1. View latest prices")
        print("  2. View price history for specific symbol")
        print("  3. View database statistics")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            limit = input("How many records to display? (default: 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            display_latest_prices(limit)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
            if symbol:
                limit = input("How many records to display? (default: 50): ").strip()
                limit = int(limit) if limit.isdigit() else 50
                display_symbol_history(symbol, limit)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            display_database_stats()
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            print("\nGoodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please try again.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='View cryptocurrency data from PostgreSQL')
    parser.add_argument(
        '--mode',
        type=str,
        choices=['latest', 'history', 'stats', 'interactive'],
        default='interactive',
        help='Viewing mode (default: interactive)'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        help='Symbol for history mode (e.g., BTCUSDT)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Number of records to display'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'latest':
        display_latest_prices(args.limit)
    elif args.mode == 'history':
        if args.symbol:
            display_symbol_history(args.symbol, args.limit)
        else:
            print("✗ Error: --symbol required for history mode")
    elif args.mode == 'stats':
        display_database_stats()
    else:
        interactive_menu()
