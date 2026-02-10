"""
Binance API Client
Handles all interactions with the Binance API
"""

import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class BinanceClient:
    """Client for interacting with Binance API"""
    
    def __init__(self):
        self.base_url = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com')
        self.api_key = os.getenv('BINANCE_API_KEY', '')
        self.api_secret = os.getenv('BINANCE_API_SECRET', '')
        self.session = requests.Session()
        
        # Set up headers if API key is provided
        if self.api_key:
            self.session.headers.update({
                'X-MBX-APIKEY': self.api_key
            })
    
    def _make_request(self, endpoint, params=None):
        """
        Make HTTP request to Binance API
        
        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters
            
        Returns:
            dict: API response
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            response = self.session.get(url, params=params)
            response_time = int((time.time() - start_time) * 1000)
            
            response.raise_for_status()
            
            print(f"✓ API Request successful: {endpoint} ({response_time}ms)")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"✗ HTTP Error: {e}")
            print(f"Response: {response.text}")
            raise
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            raise
    
    def get_server_time(self):
        """
        Get Binance server time
        
        Returns:
            dict: Server time info
        """
        endpoint = "/api/v3/time"
        return self._make_request(endpoint)
    
    def get_exchange_info(self):
        """
        Get exchange trading rules and symbol information
        
        Returns:
            dict: Exchange information
        """
        endpoint = "/api/v3/exchangeInfo"
        return self._make_request(endpoint)
    
    def get_ticker_price(self, symbol=None):
        """
        Get latest price for a symbol or all symbols
        
        Args:
            symbol (str, optional): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            dict or list: Ticker price(s)
        """
        endpoint = "/api/v3/ticker/price"
        params = {}
        
        if symbol:
            params['symbol'] = symbol
        
        return self._make_request(endpoint, params)
    
    def get_ticker_24hr(self, symbol=None):
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol (str, optional): Trading pair symbol
            
        Returns:
            dict or list: 24hr ticker statistics
        """
        endpoint = "/api/v3/ticker/24hr"
        params = {}
        
        if symbol:
            params['symbol'] = symbol
        
        return self._make_request(endpoint, params)
    
    def get_klines(self, symbol, interval='1h', limit=100, start_time=None, end_time=None):
        """
        Get kline/candlestick data
        
        Args:
            symbol (str): Trading pair symbol
            interval (str): Kline interval (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
            limit (int): Number of klines to return (max 1000)
            start_time (int, optional): Start time in milliseconds
            end_time (int, optional): End time in milliseconds
            
        Returns:
            list: Kline data
        """
        endpoint = "/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        return self._make_request(endpoint, params)
    
    def get_orderbook(self, symbol, limit=100):
        """
        Get order book (market depth)
        
        Args:
            symbol (str): Trading pair symbol
            limit (int): Order book depth (5, 10, 20, 50, 100, 500, 1000, 5000)
            
        Returns:
            dict: Order book data
        """
        endpoint = "/api/v3/depth"
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        return self._make_request(endpoint, params)
    
    def get_recent_trades(self, symbol, limit=100):
        """
        Get recent trades
        
        Args:
            symbol (str): Trading pair symbol
            limit (int): Number of trades (max 1000)
            
        Returns:
            list: Recent trades
        """
        endpoint = "/api/v3/trades"
        params = {
            'symbol': symbol,
            'limit': limit
        }
        
        return self._make_request(endpoint, params)
    
    def get_average_price(self, symbol):
        """
        Get current average price for a symbol
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            dict: Average price info
        """
        endpoint = "/api/v3/avgPrice"
        params = {'symbol': symbol}
        
        return self._make_request(endpoint, params)
    
    def ping(self):
        """
        Test connectivity to the API
        
        Returns:
            dict: Empty dict if successful
        """
        endpoint = "/api/v3/ping"
        return self._make_request(endpoint)


# Usage example
if __name__ == "__main__":
    client = BinanceClient()
    
    print("=== Testing Binance API Client ===\n")
    
    # Test 1: Ping
    print("1. Testing API connectivity...")
    try:
        client.ping()
        print("   ✓ API is reachable\n")
    except Exception as e:
        print(f"   ✗ API ping failed: {e}\n")
    
    # Test 2: Get server time
    print("2. Getting server time...")
    try:
        server_time = client.get_server_time()
        timestamp = server_time['serverTime']
        dt = datetime.fromtimestamp(timestamp / 1000)
        print(f"   Server time: {dt}\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")
    
    # Test 3: Get Bitcoin price
    print("3. Getting Bitcoin price...")
    try:
        btc_price = client.get_ticker_price('BTCUSDT')
        print(f"   BTC Price: ${btc_price['price']}\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")
    
    # Test 4: Get 24hr stats for Ethereum
    print("4. Getting Ethereum 24hr statistics...")
    try:
        eth_stats = client.get_ticker_24hr('ETHUSDT')
        print(f"   ETH Price: ${eth_stats['lastPrice']}")
        print(f"   24h Change: {eth_stats['priceChangePercent']}%")
        print(f"   24h Volume: {eth_stats['volume']} ETH\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")
    
    # Test 5: Get latest klines
    print("5. Getting latest klines for BTC (1h interval)...")
    try:
        klines = client.get_klines('BTCUSDT', interval='1h', limit=5)
        print(f"   Retrieved {len(klines)} klines")
        print(f"   Latest close price: ${klines[-1][4]}\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")
    
    print("=== Testing Complete ===")
