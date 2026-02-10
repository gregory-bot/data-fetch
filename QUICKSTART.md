# Quick Start Guide

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Set Up PostgreSQL
```bash
# Create database
psql -U postgres
CREATE DATABASE binance_data;
\q

# Load schema
psql -U postgres -d binance_data -f database/schema.sql
```

## Step 3: Configure Environment
```bash
# Copy example file
copy .env.example .env

# Edit .env with your database password
```

## Step 4: Fetch Data
```bash
# Fetch current prices
python scripts/fetch_prices.py

# Fetch historical data
python scripts/fetch_historical.py --symbol BTCUSDT --days 7

# View data
python scripts/view_data.py
```

## Common Commands

### Fetch Specific Symbols
```bash
python scripts/fetch_prices.py --symbols BTCUSDT,ETHUSDT,BNBUSDT
```

### Fetch Top 20 Symbols
```bash
python scripts/fetch_prices.py --all
```

### Fetch Historical Data (Different Intervals)
```bash
# 1 hour candles for 7 days
python scripts/fetch_historical.py --symbol BTCUSDT --interval 1h --days 7

# 5 minute candles for 1 day
python scripts/fetch_historical.py --symbol ETHUSDT --interval 5m --days 1
```

### View Data
```bash
# Latest prices
python scripts/view_data.py --mode latest --limit 20

# Symbol history
python scripts/view_data.py --mode history --symbol BTCUSDT --limit 50

# Database statistics
python scripts/view_data.py --mode stats

# Interactive mode
python scripts/view_data.py
```

## Database Queries

### Connect to Database
```bash
psql -U postgres -d binance_data
```

### Useful Queries
```sql
-- View latest prices
SELECT * FROM v_latest_prices;

-- View specific symbol history
SELECT * FROM ticker_prices 
WHERE symbol = 'BTCUSDT' 
ORDER BY timestamp DESC 
LIMIT 10;

-- View API statistics
SELECT * FROM v_api_stats;

-- Count records
SELECT 
    'ticker_prices' as table_name, COUNT(*) as count 
FROM ticker_prices
UNION ALL
SELECT 'klines', COUNT(*) FROM klines;
```

## Troubleshooting

### "Connection refused" Error
1. Check PostgreSQL is running
2. Verify credentials in .env file
3. Test connection: `psql -U postgres`

### "Module not found" Error
```bash
# Make sure you're in virtual environment
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Table does not exist" Error
```bash
# Load the schema
psql -U postgres -d binance_data -f database/schema.sql
```
