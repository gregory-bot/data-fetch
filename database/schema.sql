-- ===========================================
-- BINANCE DATA STORAGE SCHEMA
-- ===========================================
-- PostgreSQL database schema for storing cryptocurrency data from Binance API
-- 
-- Created: 2026
-- Database: binance_data
-- 
-- Usage:
--   psql -U postgres -d binance_data -f schema.sql

-- ===========================================
-- DROP EXISTING TABLES (if needed)
-- ===========================================
-- Uncomment these lines if you want to recreate tables from scratch
-- WARNING: This will delete all existing data!

-- DROP TABLE IF EXISTS api_requests_log CASCADE;
-- DROP TABLE IF EXISTS klines CASCADE;
-- DROP TABLE IF EXISTS ticker_prices CASCADE;
-- DROP TABLE IF EXISTS trading_pairs CASCADE;


-- ===========================================
-- TABLE 1: TRADING PAIRS
-- ===========================================
-- Store information about cryptocurrency trading pairs we're tracking

CREATE TABLE IF NOT EXISTS trading_pairs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    base_asset VARCHAR(10) NOT NULL,         -- e.g., BTC
    quote_asset VARCHAR(10) NOT NULL,        -- e.g., USDT
    status VARCHAR(20) DEFAULT 'ACTIVE',     -- ACTIVE, INACTIVE
    is_spot_trading BOOLEAN DEFAULT TRUE,
    is_margin_trading BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO trading_pairs (symbol, base_asset, quote_asset) 
VALUES 
    ('BTCUSDT', 'BTC', 'USDT'),
    ('ETHUSDT', 'ETH', 'USDT'),
    ('BNBUSDT', 'BNB', 'USDT'),
    ('ADAUSDT', 'ADA', 'USDT'),
    ('DOGEUSDT', 'DOGE', 'USDT')
ON CONFLICT (symbol) DO NOTHING;


-- ===========================================
-- TABLE 2: TICKER PRICES (24hr Price Snapshots)
-- ===========================================
-- Store 24-hour ticker price statistics from Binance

CREATE TABLE IF NOT EXISTS ticker_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    
    -- Price Information
    price DECIMAL(20, 8) NOT NULL,                    -- Current price
    price_change DECIMAL(20, 8),                      -- Absolute price change
    price_change_percent DECIMAL(10, 4),              -- Price change percentage
    weighted_avg_price DECIMAL(20, 8),                -- Weighted average price
    
    -- High/Low Information
    high_price DECIMAL(20, 8),                        -- 24h high
    low_price DECIMAL(20, 8),                         -- 24h low
    
    -- Opening/Closing Prices
    open_price DECIMAL(20, 8),                        -- Opening price
    last_price DECIMAL(20, 8),                        -- Last price
    
    -- Volume Information
    volume DECIMAL(30, 8),                            -- 24h trading volume (base asset)
    quote_volume DECIMAL(30, 8),                      -- 24h trading volume (quote asset)
    
    -- Bid/Ask Information
    bid_price DECIMAL(20, 8),                         -- Best bid price
    bid_qty DECIMAL(30, 8),                           -- Best bid quantity
    ask_price DECIMAL(20, 8),                         -- Best ask price
    ask_qty DECIMAL(30, 8),                           -- Best ask quantity
    
    -- Trading Information
    num_trades BIGINT,                                -- Number of trades
    open_time BIGINT,                                 -- Open time (timestamp)
    close_time BIGINT,                                -- Close time (timestamp)
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- When we fetched this data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to trading_pairs table
    CONSTRAINT fk_ticker_symbol 
        FOREIGN KEY (symbol) 
        REFERENCES trading_pairs(symbol)
        ON DELETE CASCADE
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ticker_symbol ON ticker_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_ticker_timestamp ON ticker_prices(timestamp);
CREATE INDEX IF NOT EXISTS idx_ticker_symbol_timestamp ON ticker_prices(symbol, timestamp DESC);


-- ===========================================
-- TABLE 3: KLINES (Candlestick Data)
-- ===========================================
-- Store historical candlestick (OHLCV) data

CREATE TABLE IF NOT EXISTS klines (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,              -- 1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M
    
    -- Candlestick Data (OHLCV)
    open_time BIGINT NOT NULL,                  -- Kline open time (timestamp)
    open_price DECIMAL(20, 8) NOT NULL,         -- Opening price
    high_price DECIMAL(20, 8) NOT NULL,         -- Highest price
    low_price DECIMAL(20, 8) NOT NULL,          -- Lowest price
    close_price DECIMAL(20, 8) NOT NULL,        -- Closing price
    volume DECIMAL(30, 8) NOT NULL,             -- Trading volume
    
    -- Additional Information
    close_time BIGINT NOT NULL,                 -- Kline close time
    quote_asset_volume DECIMAL(30, 8),          -- Quote asset volume
    num_trades INTEGER,                         -- Number of trades
    taker_buy_base_volume DECIMAL(30, 8),       -- Taker buy base asset volume
    taker_buy_quote_volume DECIMAL(30, 8),      -- Taker buy quote asset volume
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite unique constraint (prevent duplicate klines)
    UNIQUE(symbol, interval, open_time),
    
    -- Foreign key
    CONSTRAINT fk_kline_symbol 
        FOREIGN KEY (symbol) 
        REFERENCES trading_pairs(symbol)
        ON DELETE CASCADE
);

-- Indexes for historical data queries
CREATE INDEX IF NOT EXISTS idx_klines_symbol ON klines(symbol);
CREATE INDEX IF NOT EXISTS idx_klines_interval ON klines(interval);
CREATE INDEX IF NOT EXISTS idx_klines_open_time ON klines(open_time);
CREATE INDEX IF NOT EXISTS idx_klines_composite ON klines(symbol, interval, open_time DESC);


-- ===========================================
-- TABLE 4: API REQUEST LOG
-- ===========================================
-- Track API requests for monitoring and debugging

CREATE TABLE IF NOT EXISTS api_requests_log (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,             -- API endpoint called
    method VARCHAR(10) DEFAULT 'GET',           -- HTTP method
    
    -- Request Information
    request_params TEXT,                        -- JSON string of parameters
    
    -- Response Information
    status_code INTEGER,                        -- HTTP status code
    response_time_ms INTEGER,                   -- Response time in milliseconds
    success BOOLEAN DEFAULT TRUE,               -- Whether request was successful
    error_message TEXT,                         -- Error message if failed
    
    -- Rate Limiting
    weight INTEGER,                             -- API weight used
    rate_limit_remaining INTEGER,               -- Remaining rate limit
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for monitoring queries
CREATE INDEX IF NOT EXISTS idx_api_log_created ON api_requests_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_log_endpoint ON api_requests_log(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_log_success ON api_requests_log(success);


-- ===========================================
-- TABLE 5: DATA FETCH SCHEDULE
-- ===========================================
-- Track scheduled data fetching jobs

CREATE TABLE IF NOT EXISTS fetch_schedule (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- Schedule Information
    interval_seconds INTEGER NOT NULL,           -- How often to run (in seconds)
    last_run TIMESTAMP,                         -- Last execution time
    next_run TIMESTAMP,                         -- Next scheduled run
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'PENDING',       -- PENDING, RUNNING, COMPLETED, FAILED
    
    -- Statistics
    total_runs INTEGER DEFAULT 0,
    successful_runs INTEGER DEFAULT 0,
    failed_runs INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample schedule entries
INSERT INTO fetch_schedule (job_name, description, interval_seconds) 
VALUES 
    ('fetch_ticker_prices', 'Fetch 24hr ticker prices for all pairs', 60),
    ('fetch_1m_klines', 'Fetch 1-minute klines data', 60),
    ('fetch_1h_klines', 'Fetch 1-hour klines data', 3600)
ON CONFLICT (job_name) DO NOTHING;


-- ===========================================
-- USEFUL VIEWS
-- ===========================================

-- View: Latest prices for all symbols
CREATE OR REPLACE VIEW v_latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol,
    price,
    price_change_percent,
    high_price,
    low_price,
    volume,
    timestamp
FROM ticker_prices
ORDER BY symbol, timestamp DESC;


-- View: Latest klines for each symbol and interval
CREATE OR REPLACE VIEW v_latest_klines AS
SELECT DISTINCT ON (symbol, interval)
    symbol,
    interval,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    to_timestamp(open_time/1000) as open_time,
    to_timestamp(close_time/1000) as close_time
FROM klines
ORDER BY symbol, interval, open_time DESC;


-- View: API request statistics
CREATE OR REPLACE VIEW v_api_stats AS
SELECT 
    endpoint,
    COUNT(*) as total_requests,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests,
    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed_requests,
    ROUND(AVG(response_time_ms), 2) as avg_response_time_ms,
    MAX(created_at) as last_request
FROM api_requests_log
GROUP BY endpoint
ORDER BY total_requests DESC;


-- ===========================================
-- USEFUL FUNCTIONS
-- ===========================================

-- Function to clean old data (keep only last 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 30)
RETURNS TABLE(
    table_name TEXT,
    rows_deleted BIGINT
) AS $$
DECLARE
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
    
    -- Clean ticker_prices
    DELETE FROM ticker_prices WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    table_name := 'ticker_prices';
    RETURN NEXT;
    
    -- Clean klines
    DELETE FROM klines WHERE created_at < cutoff_date;
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    table_name := 'klines';
    RETURN NEXT;
    
    -- Clean api_requests_log
    DELETE FROM api_requests_log WHERE created_at < cutoff_date;
    GET DIAGNOSTICS rows_deleted = ROW_COUNT;
    table_name := 'api_requests_log';
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;


-- ===========================================
-- GRANT PERMISSIONS
-- ===========================================
-- Grant necessary permissions to the postgres user
-- Adjust if you're using a different user

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;


-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================
-- Run these to verify your setup

-- Show all tables
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Count records in each table
-- SELECT 'ticker_prices' as table_name, COUNT(*) as count FROM ticker_prices
-- UNION ALL
-- SELECT 'klines', COUNT(*) FROM klines
-- UNION ALL
-- SELECT 'api_requests_log', COUNT(*) FROM api_requests_log
-- UNION ALL
-- SELECT 'trading_pairs', COUNT(*) FROM trading_pairs;

-- View latest prices
-- SELECT * FROM v_latest_prices;

-- ===========================================
-- SETUP COMPLETE!
-- ===========================================
-- Your database schema is now ready to use.
-- Next steps:
-- 1. Configure your .env file with database credentials
-- 2. Run the Python scripts to start fetching data
-- 3. Use the queries above to view your data
