# Binance API Data Fetching & PostgreSQL Storage Guide

guide to fetch cryptocurrency data from Binance API and store it in PostgreSQL database.

## 📋 Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Database Configuration](#database-configuration)
- [Running the Application](#running-the-application)
- [Viewing Your Data](#viewing-your-data)
- [Common Issues & Solutions](#common-issues--solutions)

## 🎯 Overview

This project demonstrates how to:
- Fetch real-time cryptocurrency data from Binance API
- Store the data in a PostgreSQL database
- Set up proper database schemas
- Handle API requests efficiently
- Manage environment variables securely

## Prerequisites

have the following installed:

1. **Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **PostgreSQL 12+**
   - Download from [postgresql.org](https://www.postgresql.org/download/)
   - During installation, remember your password!
   - Verify installation: `psql --version`

3. **pip** (Python package manager)
   - Usually comes with Python
   - Verify: `pip --version`

## Project Structure

```
binance/
│
├── README.md                 # This file
├── .env                      # Your configuration (DO NOT commit to git!)
├── .env.example             # Template for environment variables
├── .gitignore               # Files to ignore in git
│
├── requirements.txt         # Python dependencies
├── database/
│   ├── schema.sql          # Database table definitions
│   └── connection.py       # Database connection handler
│
├── api/
│   ├── binance_client.py   # Binance API functions
│   └── config.py           # API configuration
│
├── scripts/
│   ├── fetch_prices.py     # Fetch current prices
│   └── fetch_historical.py # Fetch historical data
│
└── notebooks/
    ├── fetchdata.ipynb     # Interactive data fetching
    └── setup-db.ipynb      # Database setup notebook
```

## Instructions

### Step 1: Clone or Create Project Directory

```bash
# If starting fresh, create the directory
mkdir binance
cd binance
```

### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Required Packages

Create a `requirements.txt` file with:
```
requests==2.31.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pandas==2.1.4
```

Install packages:
```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL Database

1. **Open PostgreSQL Command Line** (psql):
   ```bash
   psql -U postgres
   ```

2. **Create a new database**:
   ```sql
   CREATE DATABASE binance_data;
   ```

3. **Exit psql**:
   ```sql
   \q
   ```

### Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env    # Windows
   cp .env.example .env      # Mac/Linux
   ```

2. Edit `.env` with your actual credentials:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=binance_data
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password

   # Binance API (Optional - public endpoints don't need keys)
   BINANCE_API_KEY=
   BINANCE_API_SECRET=
   ```

### Step 6: Create Database Schema

Run the schema creation script:
```bash
psql -U postgres -d binance_data -f database/schema.sql
```

Or use the notebook: `setup-db.ipynb`

## Database Configuration

### Understanding the Schema

The `schema.sql` creates tables to store:

1. **ticker_prices** - Real-time price snapshots
   - Symbol (e.g., BTCUSDT)
   - Current price
   - 24h high/low
   - Trading volume
   - Timestamp

2. **klines** - Historical candlestick data
   - Open, High, Low, Close prices
   - Volume
   - Time intervals (1m, 5m, 1h, 1d)

3. **api_requests_log** - Track API calls
   - Endpoint called
   - Response time
   - Status code
   - Timestamp

### Schema Structure

```sql
-- Ticker prices table
CREATE TABLE ticker_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    price_change DECIMAL(20, 8),
    price_change_percent DECIMAL(10, 4),
    high_price DECIMAL(20, 8),
    low_price DECIMAL(20, 8),
    volume DECIMAL(30, 8),
    quote_volume DECIMAL(30, 8),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX idx_ticker_symbol ON ticker_prices(symbol);
CREATE INDEX idx_ticker_timestamp ON ticker_prices(timestamp);
```

## Running the Application

### Fetch Current Prices

```bash
python scripts/fetch_prices.py
```

This will:
- Connect to Binance API
- Fetch current prices for major cryptocurrencies
- Store data in PostgreSQL
- Display confirmation

### Fetch Historical Data

```bash
python scripts/fetch_historical.py
```

### Using Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook

# Open fetchdata.ipynb
# Run cells step by step to see the process
```

## Viewing Your Data

### Option 1: Using psql Command Line

```bash
# Connect to database
psql -U postgres -d binance_data

# View all tables
\dt

# Query recent prices
SELECT symbol, price, timestamp 
FROM ticker_prices 
ORDER BY timestamp DESC 
LIMIT 10;

# Query specific cryptocurrency
SELECT * FROM ticker_prices 
WHERE symbol = 'BTCUSDT' 
ORDER BY timestamp DESC 
LIMIT 5;

# Count total records
SELECT COUNT(*) FROM ticker_prices;
```

### Option 2: Using pgAdmin

1. Open pgAdmin (installed with PostgreSQL)
2. Connect to your server (localhost)
3. Navigate to: Servers → PostgreSQL → Databases → binance_data → Schemas → public → Tables
4. Right-click on a table → View/Edit Data → All Rows

### Option 3: Using Python Script

Create `view_data.py`:
```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)

cur = conn.cursor()
cur.execute("SELECT * FROM ticker_prices ORDER BY timestamp DESC LIMIT 10")
rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()
```

* ### gregory.tech: The best way to learn is by doing. Don't be afraid to experiment and make mistakes!*
