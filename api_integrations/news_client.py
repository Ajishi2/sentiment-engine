"""
News API integration for financial news sentiment analysis
"""
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from config import api_config, data_config
from core.data_models import RawData, DataSource

logger = logging.getLogger(__name__)

class NewsAPIClient:
    """News API client for financial news aggregation"""
    
    def __init__(self):
        self.api_key = api_config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
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
    
    async def get_financial_news(self, query: str = None, sources: List[str] = None, 
                                language: str = 'en', page_size: int = 100) -> List[RawData]:
        """Get financial news articles"""
        if self.api_key == 'demo_key':
            return await self._generate_mock_news(page_size)
        
        await self.start_session()
        
        try:
            url = f"{self.base_url}/everything"
            
            # Default financial query if none provided
            if not query:
                query = "bitcoin OR cryptocurrency OR stocks OR trading OR investing OR market OR finance"
            
            params = {
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',
                'pageSize': min(page_size, 100),
                'apiKey': self.api_key
            }
            
            if sources:
                params['sources'] = ','.join(sources)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_news_response(data)
                else:
                    logger.error(f"News API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    async def get_top_headlines(self, category: str = 'business', 
                               country: str = 'us', page_size: int = 50) -> List[RawData]:
        """Get top headlines"""
        if self.api_key == 'demo_key':
            return await self._generate_mock_headlines(page_size)
        
        await self.start_session()
        
        try:
            url = f"{self.base_url}/top-headlines"
            
            params = {
                'category': category,
                'country': country,
                'pageSize': min(page_size, 100),
                'apiKey': self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_news_response(data)
                else:
                    logger.error(f"Headlines API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching headlines: {e}")
            return []
    
    async def stream_financial_news(self, update_interval: int = 300) -> List[RawData]:
        """Stream financial news with regular updates"""
        while True:
            try:
                # Get recent financial news
                news_articles = await self.get_financial_news(page_size=20)
                
                # Get business headlines
                headlines = await self.get_top_headlines(page_size=10)
                
                # Combine and return
                all_news = news_articles + headlines
                
                # Remove duplicates based on URL
                seen_urls = set()
                unique_news = []
                for article in all_news:
                    url = article.metadata.get('url', '')
                    if url not in seen_urls:
                        seen_urls.add(url)
                        unique_news.append(article)
                
                return unique_news
                
            except Exception as e:
                logger.error(f"Error in news stream: {e}")
                return []
            finally:
                await asyncio.sleep(update_interval)
    
    def _parse_news_response(self, data: Dict) -> List[RawData]:
        """Parse News API response into RawData objects"""
        raw_data_list = []
        
        try:
            articles = data.get('articles', [])
            
            for article in articles:
                # Skip articles without content
                if not article.get('title') or article.get('title') == '[Removed]':
                    continue
                
                # Combine title and description
                content = article['title']
                if article.get('description'):
                    content += f" {article['description']}"
                
                # Parse timestamp
                published_at = article.get('publishedAt')
                if published_at:
                    timestamp = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.now()
                
                raw_data = RawData(
                    id=f"news_{hash(article.get('url', content))}",
                    source=DataSource.NEWS,
                    timestamp=timestamp,
                    content=content,
                    author=article.get('author', article.get('source', {}).get('name', 'Unknown')),
                    metadata={
                        'url': article.get('url', ''),
                        'source_name': article.get('source', {}).get('name', ''),
                        'source_id': article.get('source', {}).get('id', ''),
                        'url_to_image': article.get('urlToImage', ''),
                        'content_snippet': article.get('content', '')[:200] if article.get('content') else ''
                    }
                )
                
                raw_data_list.append(raw_data)
                
        except Exception as e:
            logger.error(f"Error parsing news response: {e}")
        
        return raw_data_list
    
    async def _generate_mock_news(self, count: int) -> List[RawData]:
        """Generate mock news articles for demo"""
        mock_headlines = [
            "Bitcoin Surges Past $50K as Institutional Demand Continues to Grow",
            "Federal Reserve Hints at Interest Rate Changes Affecting Crypto Markets",
            "Major Investment Bank Announces Comprehensive Cryptocurrency Trading Services",
            "Regulatory Clarity Boosts Market Confidence in Digital Assets Sector",
            "Technology Stocks Rally on Positive Quarterly Earnings Reports",
            "Market Volatility Increases Amid Global Economic Uncertainty Concerns",
            "Ethereum Network Upgrade Shows Promising Performance Improvements",
            "Investment Firm Predicts Bullish Long-term Outlook for Blockchain Technology",
            "Central Bank Digital Currency Pilot Program Shows Promising Results",
            "Cryptocurrency Adoption Accelerates Among Fortune 500 Companies"
        ]
        
        mock_descriptions = [
            "Market analysts report increased institutional interest driving price momentum upward.",
            "Economic indicators suggest potential policy changes could impact digital asset valuations.",
            "Financial services expansion into cryptocurrency markets signals growing mainstream adoption.",
            "Clear regulatory framework provides foundation for sustainable market growth.",
            "Strong earnings performance across technology sector boosts investor confidence.",
            "Global economic factors contribute to increased market volatility and uncertainty.",
            "Technical improvements demonstrate continued innovation in blockchain infrastructure.",
            "Long-term investment strategies increasingly include digital asset allocations.",
            "Government-backed digital currency trials show potential for widespread implementation.",
            "Corporate treasury diversification strategies now commonly include cryptocurrency holdings."
        ]
        
        import random
        news_articles = []
        for i in range(count):
            headline = random.choice(mock_headlines)
            description = random.choice(mock_descriptions)
            
            news_articles.append(RawData(
                id=f"mock_news_{datetime.now().timestamp()}_{i}",
                source=DataSource.NEWS,
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 1440)),
                content=f"{headline} {description}",
                author=random.choice(["Financial Times", "Reuters", "Bloomberg", "CNBC", "MarketWatch"]),
                metadata={
                    'url': f"https://example.com/news/{i}",
                    'source_name': random.choice(["Financial Times", "Reuters", "Bloomberg"]),
                    'category': 'finance'
                }
            ))
        
        return news_articles
    
    async def _generate_mock_headlines(self, count: int) -> List[RawData]:
        """Generate mock headlines for demo"""
        mock_headlines = [
            "Stock Market Opens Higher on Positive Economic Data",
            "Cryptocurrency Market Shows Signs of Recovery",
            "Tech Giants Report Strong Quarterly Performance",
            "Federal Reserve Maintains Current Interest Rate Policy",
            "Global Markets React to Geopolitical Developments",
            "Energy Sector Leads Market Gains in Early Trading",
            "Banking Stocks Rise on Improved Credit Conditions",
            "Consumer Confidence Index Reaches New Monthly High"
        ]
        
        import random
        headlines = []
        for i in range(count):
            headline = random.choice(mock_headlines)
            
            headlines.append(RawData(
                id=f"mock_headline_{datetime.now().timestamp()}_{i}",
                source=DataSource.NEWS,
                timestamp=datetime.now() - timedelta(minutes=random.randint(0, 360)),
                content=headline,
                author="News Wire",
                metadata={
                    'url': f"https://example.com/headline/{i}",
                    'source_name': "Business News",
                    'category': 'business'
                }
            ))
        
        return headlines

class AlphaVantageNewsClient:
    """Alpha Vantage News API client for additional financial news"""
    
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
    
    async def get_news_sentiment(self, tickers: List[str] = None, 
                                topics: List[str] = None, limit: int = 50) -> List[RawData]:
        """Get news sentiment data from Alpha Vantage"""
        if self.api_key == 'demo_key':
            return await self._generate_mock_sentiment_news(limit)
        
        await self.start_session()
        
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'limit': limit
            }
            
            if tickers:
                params['tickers'] = ','.join(tickers)
            
            if topics:
                params['topics'] = ','.join(topics)
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_sentiment_response(data)
                else:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage news: {e}")
            return []
    
    def _parse_sentiment_response(self, data: Dict) -> List[RawData]:
        """Parse Alpha Vantage news sentiment response"""
        raw_data_list = []
        
        try:
            feed = data.get('feed', [])
            
            for article in feed:
                # Combine title and summary
                content = article.get('title', '')
                if article.get('summary'):
                    content += f" {article['summary']}"
                
                # Parse timestamp
                time_published = article.get('time_published')
                if time_published:
                    # Alpha Vantage format: YYYYMMDDTHHMMSS
                    timestamp = datetime.strptime(time_published, '%Y%m%dT%H%M%S')
                else:
                    timestamp = datetime.now()
                
                raw_data = RawData(
                    id=f"alphavantage_{hash(article.get('url', content))}",
                    source=DataSource.NEWS,
                    timestamp=timestamp,
                    content=content,
                    author=article.get('source', 'Alpha Vantage'),
                    metadata={
                        'url': article.get('url', ''),
                        'source': article.get('source', ''),
                        'overall_sentiment_score': article.get('overall_sentiment_score', 0),
                        'overall_sentiment_label': article.get('overall_sentiment_label', 'Neutral'),
                        'ticker_sentiment': article.get('ticker_sentiment', []),
                        'topics': article.get('topics', [])
                    }
                )
                
                raw_data_list.append(raw_data)
                
        except Exception as e:
            logger.error(f"Error parsing Alpha Vantage response: {e}")
        
        return raw_data_list
    
    async def _generate_mock_sentiment_news(self, count: int) -> List[RawData]:
        """Generate mock sentiment news for demo"""
        # This would be similar to the NewsAPI mock data
        # but with sentiment scores included
        return []