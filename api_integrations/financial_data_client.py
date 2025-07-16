"""
Financial data API integration for market data and correlation analysis
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yfinance as yf
import json

from config import api_config, data_config
from core.data_models import MarketData

logger = logging.getLogger(__name__)

class FinancialDataClient:
    """Financial data client for market data collection"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start_session(self):
        """Start HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_stock_data(self, symbols: List[str]) -> List[MarketData]:
        """Get stock market data using yfinance"""
        market_data_list = []
        
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d", interval="1m")
                
                if not hist.empty:
                    latest = hist.iloc[-1]
                    
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        price=float(latest['Close']),
                        volume=float(latest['Volume']),
                        change_24h=float((latest['Close'] - hist.iloc[0]['Open']) / hist.iloc[0]['Open']),
                        market_cap=info.get('marketCap'),
                        additional_metrics={
                            'high_24h': float(hist['High'].max()),
                            'low_24h': float(hist['Low'].min()),
                            'open': float(hist.iloc[0]['Open']),
                            'previous_close': float(info.get('previousClose', latest['Close']))
                        }
                    )
                    
                    market_data_list.append(market_data)
                    
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            # Return mock data for demo
            return await self._generate_mock_stock_data(symbols)
        
        return market_data_list
    
    async def get_crypto_data(self, symbols: List[str]) -> List[MarketData]:
        """Get cryptocurrency data from CoinGecko API"""
        await self.start_session()
        
        try:
            # Convert symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'SOL': 'solana',
                'MATIC': 'polygon',
                'DOGE': 'dogecoin',
                'XRP': 'ripple'
            }
            
            coin_ids = [symbol_map.get(symbol.upper(), symbol.lower()) for symbol in symbols]
            ids_string = ','.join(coin_ids)
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': ids_string,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_coingecko_data(data, symbols, symbol_map)
                else:
                    logger.error(f"CoinGecko API error: {response.status}")
                    return await self._generate_mock_crypto_data(symbols)
                    
        except Exception as e:
            logger.error(f"Error fetching crypto data: {e}")
            return await self._generate_mock_crypto_data(symbols)
    
    def _parse_coingecko_data(self, data: Dict, symbols: List[str], symbol_map: Dict) -> List[MarketData]:
        """Parse CoinGecko API response"""
        market_data_list = []
        
        for symbol in symbols:
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            coin_data = data.get(coin_id, {})
            
            if coin_data:
                market_data = MarketData(
                    symbol=symbol.upper(),
                    timestamp=datetime.now(),
                    price=coin_data.get('usd', 0),
                    volume=coin_data.get('usd_24h_vol', 0),
                    change_24h=coin_data.get('usd_24h_change', 0) / 100,  # Convert percentage
                    market_cap=coin_data.get('usd_market_cap'),
                    additional_metrics={
                        'source': 'coingecko',
                        'last_updated': datetime.now().isoformat()
                    }
                )
                
                market_data_list.append(market_data)
        
        return market_data_list
    
    async def get_market_overview(self) -> Dict:
        """Get overall market overview"""
        await self.start_session()
        
        try:
            # Get crypto market overview
            url = "https://api.coingecko.com/api/v3/global"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    global_data = data.get('data', {})
                    
                    return {
                        'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd', 0),
                        'total_volume_24h_usd': global_data.get('total_volume', {}).get('usd', 0),
                        'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd', 0),
                        'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                        'markets': global_data.get('markets', 0),
                        'market_cap_percentage': global_data.get('market_cap_percentage', {}),
                        'updated_at': datetime.now().isoformat()
                    }
                else:
                    logger.error(f"Market overview API error: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching market overview: {e}")
            return {}
    
    async def stream_market_data(self, symbols: List[str], update_interval: int = 60) -> List[MarketData]:
        """Stream market data with regular updates"""
        while True:
            try:
                # Get stock data
                stock_symbols = [s for s in symbols if s.upper() in data_config.STOCK_SYMBOLS]
                crypto_symbols = [s for s in symbols if s.upper() in data_config.CRYPTO_SYMBOLS]
                
                all_data = []
                
                if stock_symbols:
                    stock_data = await self.get_stock_data(stock_symbols)
                    all_data.extend(stock_data)
                
                if crypto_symbols:
                    crypto_data = await self.get_crypto_data(crypto_symbols)
                    all_data.extend(crypto_data)
                
                return all_data
                
            except Exception as e:
                logger.error(f"Error in market data stream: {e}")
                return []
            finally:
                await asyncio.sleep(update_interval)
    
    async def _generate_mock_stock_data(self, symbols: List[str]) -> List[MarketData]:
        """Generate mock stock data for demo"""
        import random
        
        mock_data = []
        base_prices = {'AAPL': 150, 'GOOGL': 2500, 'MSFT': 300, 'TSLA': 800, 'AMZN': 3000}
        
        for symbol in symbols:
            base_price = base_prices.get(symbol, random.uniform(50, 500))
            current_price = base_price * random.uniform(0.95, 1.05)
            
            mock_data.append(MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=current_price,
                volume=random.uniform(1000000, 50000000),
                change_24h=random.uniform(-0.1, 0.1),
                market_cap=current_price * random.uniform(1e9, 1e12),
                additional_metrics={
                    'high_24h': current_price * random.uniform(1.0, 1.05),
                    'low_24h': current_price * random.uniform(0.95, 1.0),
                    'source': 'mock_data'
                }
            ))
        
        return mock_data
    
    async def _generate_mock_crypto_data(self, symbols: List[str]) -> List[MarketData]:
        """Generate mock crypto data for demo"""
        import random
        
        mock_data = []
        base_prices = {'BTC': 45000, 'ETH': 3000, 'ADA': 1.2, 'SOL': 100, 'MATIC': 0.8}
        
        for symbol in symbols:
            base_price = base_prices.get(symbol.upper(), random.uniform(0.1, 1000))
            current_price = base_price * random.uniform(0.9, 1.1)
            
            mock_data.append(MarketData(
                symbol=symbol.upper(),
                timestamp=datetime.now(),
                price=current_price,
                volume=random.uniform(100000000, 10000000000),
                change_24h=random.uniform(-0.15, 0.15),
                market_cap=current_price * random.uniform(1e9, 1e12),
                additional_metrics={
                    'source': 'mock_data',
                    'volatility': random.uniform(0.02, 0.08)
                }
            ))
        
        return mock_data

class AlphaVantageClient:
    """Alpha Vantage API client for additional financial data"""
    
    def __init__(self):
        self.api_key = api_config.ALPHA_VANTAGE_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start_session(self):
        """Start HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_intraday_data(self, symbol: str, interval: str = '5min') -> Optional[MarketData]:
        """Get intraday stock data"""
        if self.api_key == 'demo_key':
            return None
        
        await self.start_session()
        
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'apikey': self.api_key
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_intraday_data(data, symbol)
                else:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            return None
    
    def _parse_intraday_data(self, data: Dict, symbol: str) -> Optional[MarketData]:
        """Parse Alpha Vantage intraday data"""
        try:
            time_series_key = f"Time Series ({interval})"
            time_series = data.get(time_series_key, {})
            
            if not time_series:
                return None
            
            # Get the most recent data point
            latest_time = max(time_series.keys())
            latest_data = time_series[latest_time]
            
            return MarketData(
                symbol=symbol,
                timestamp=datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S'),
                price=float(latest_data['4. close']),
                volume=float(latest_data['5. volume']),
                change_24h=0,  # Would need additional calculation
                additional_metrics={
                    'open': float(latest_data['1. open']),
                    'high': float(latest_data['2. high']),
                    'low': float(latest_data['3. low']),
                    'source': 'alpha_vantage'
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing Alpha Vantage data: {e}")
            return None