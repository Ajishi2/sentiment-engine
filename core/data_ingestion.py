"""
Data ingestion module for multiple sources
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, AsyncGenerator
from abc import ABC, abstractmethod

from config import api_config, data_config
from core.data_models import RawData, DataSource

logger = logging.getLogger(__name__)

class DataIngestionBase(ABC):
    """Base class for data ingestion"""
    
    def __init__(self, source: DataSource):
        self.source = source
        self.is_running = False
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """Start the data ingestion"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        self.is_running = True
        logger.info(f"Started {self.source.value} data ingestion")
    
    async def stop(self):
        """Stop the data ingestion"""
        self.is_running = False
        if self.session:
            await self.session.close()
        logger.info(f"Stopped {self.source.value} data ingestion")
    
    @abstractmethod
    async def fetch_data(self) -> AsyncGenerator[RawData, None]:
        """Fetch data from the source"""
        pass

class TwitterIngestion(DataIngestionBase):
    """Twitter data ingestion using Twitter API v2"""
    
    def __init__(self):
        super().__init__(DataSource.TWITTER)
        self.bearer_token = api_config.TWITTER_BEARER_TOKEN
    
    async def fetch_data(self) -> AsyncGenerator[RawData, None]:
        """Fetch tweets related to financial keywords"""
        if self.bearer_token == 'demo_token':
            # Generate mock Twitter data for demo
            async for data in self._generate_mock_tweets():
                yield data
        else:
            # Real Twitter API implementation
            async for data in self._fetch_real_tweets():
                yield data
    
    async def _generate_mock_tweets(self) -> AsyncGenerator[RawData, None]:
        """Generate mock Twitter data for demonstration"""
        mock_tweets = [
            "Bitcoin is mooning! 🚀 This bull run is just getting started #BTC #crypto",
            "Major selloff in crypto markets today. Time to buy the dip? 🤔 #Bitcoin #ETH",
            "BREAKING: Major institution announces Bitcoin allocation 📈 #crypto #news",
            "Market looking very bearish right now. Time to be cautious 📉 #stocks #trading",
            "Ethereum hitting new highs! DeFi season is here 🌟 #ETH #DeFi",
            "FUD spreading everywhere but fundamentals remain strong 💪 #HODL",
            "This volatility is insane! Markets going crazy today 📊 #trading",
            "Accumulating more during this dip. Long term bullish 📈 #investing"
        ]
        
        import random
        while self.is_running:
            tweet = random.choice(mock_tweets)
            data = RawData(
                id=f"tweet_{datetime.now().timestamp()}",
                source=self.source,
                timestamp=datetime.now(),
                content=tweet,
                author=f"user_{random.randint(1000, 9999)}",
                metadata={"retweets": random.randint(0, 100), "likes": random.randint(0, 500)}
            )
            yield data
            await asyncio.sleep(random.uniform(2, 8))  # Random delay between tweets
    
    async def _fetch_real_tweets(self) -> AsyncGenerator[RawData, None]:
        """Fetch real tweets using Twitter API v2"""
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        keywords = " OR ".join(data_config.TWITTER_KEYWORDS)
        
        while self.is_running:
            try:
                # Twitter API v2 recent search endpoint
                url = "https://api.twitter.com/2/tweets/search/recent"
                params = {
                    "query": keywords,
                    "max_results": 10,
                    "tweet.fields": "created_at,author_id,public_metrics"
                }
                
                async with self.session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        for tweet in data.get("data", []):
                            yield RawData(
                                id=tweet["id"],
                                source=self.source,
                                timestamp=datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
                                content=tweet["text"],
                                author=tweet["author_id"],
                                metadata=tweet.get("public_metrics", {})
                            )
                    else:
                        logger.warning(f"Twitter API error: {response.status}")
                
                await asyncio.sleep(60)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching Twitter data: {e}")
                await asyncio.sleep(30)

class RedditIngestion(DataIngestionBase):
    """Reddit data ingestion"""
    
    def __init__(self):
        super().__init__(DataSource.REDDIT)
    
    async def fetch_data(self) -> AsyncGenerator[RawData, None]:
        """Fetch Reddit posts and comments"""
        # Generate mock Reddit data for demo
        async for data in self._generate_mock_reddit():
            yield data
    
    async def _generate_mock_reddit(self) -> AsyncGenerator[RawData, None]:
        """Generate mock Reddit data"""
        mock_posts = [
            "Just bought more BTC. This dip won't last long! Diamond hands 💎🙌",
            "Analysis: Why I think we're entering a bear market. Thoughts?",
            "DCA strategy has been working great for me. Down 20% but still buying",
            "FOMO is real right now. Should I wait for a better entry point?",
            "Technical analysis suggests we might see $100k Bitcoin soon",
            "Panic selling everywhere. This is when you separate weak from strong hands",
            "Institutional adoption is accelerating. Very bullish long term",
            "Market manipulation is obvious. Whales dumping to cause fear"
        ]
        
        import random
        while self.is_running:
            post = random.choice(mock_posts)
            data = RawData(
                id=f"reddit_{datetime.now().timestamp()}",
                source=self.source,
                timestamp=datetime.now(),
                content=post,
                author=f"redditor_{random.randint(1000, 9999)}",
                metadata={"upvotes": random.randint(-10, 100), "comments": random.randint(0, 50)}
            )
            yield data
            await asyncio.sleep(random.uniform(3, 10))

class NewsIngestion(DataIngestionBase):
    """News data ingestion"""
    
    def __init__(self):
        super().__init__(DataSource.NEWS)
        self.api_key = api_config.NEWS_API_KEY
    
    async def fetch_data(self) -> AsyncGenerator[RawData, None]:
        """Fetch financial news articles"""
        if self.api_key == 'demo_key':
            async for data in self._generate_mock_news():
                yield data
        else:
            async for data in self._fetch_real_news():
                yield data
    
    async def _generate_mock_news(self) -> AsyncGenerator[RawData, None]:
        """Generate mock news data"""
        mock_headlines = [
            "Bitcoin Surges Past $50K as Institutional Demand Grows",
            "Federal Reserve Hints at Interest Rate Changes Affecting Crypto Markets",
            "Major Bank Announces Cryptocurrency Trading Services",
            "Regulatory Clarity Boosts Market Confidence in Digital Assets",
            "Tech Stocks Rally on Positive Earnings Reports",
            "Market Volatility Increases Amid Global Economic Uncertainty",
            "Ethereum Upgrade Shows Promising Network Improvements",
            "Investment Firm Predicts Bullish Outlook for Blockchain Technology"
        ]
        
        import random
        while self.is_running:
            headline = random.choice(mock_headlines)
            data = RawData(
                id=f"news_{datetime.now().timestamp()}",
                source=self.source,
                timestamp=datetime.now(),
                content=headline,
                author="Financial Times",
                metadata={"category": "finance", "source": "demo_news"}
            )
            yield data
            await asyncio.sleep(random.uniform(30, 120))  # News comes less frequently
    
    async def _fetch_real_news(self) -> AsyncGenerator[RawData, None]:
        """Fetch real news using NewsAPI"""
        while self.is_running:
            try:
                keywords = "bitcoin OR cryptocurrency OR blockchain OR stocks OR trading"
                url = f"https://newsapi.org/v2/everything?q={keywords}&apiKey={self.api_key}&language=en&sortBy=publishedAt"
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for article in data.get("articles", []):
                            yield RawData(
                                id=article["url"],
                                source=self.source,
                                timestamp=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00")),
                                content=f"{article['title']} {article.get('description', '')}",
                                author=article.get("author", "Unknown"),
                                metadata={"source": article["source"]["name"], "url": article["url"]}
                            )
                    else:
                        logger.warning(f"News API error: {response.status}")
                
                await asyncio.sleep(300)  # Check for news every 5 minutes
            except Exception as e:
                logger.error(f"Error fetching news data: {e}")
                await asyncio.sleep(60)

class FinancialDataIngestion(DataIngestionBase):
    """Financial market data ingestion"""
    
    def __init__(self):
        super().__init__(DataSource.FINANCIAL)
    
    async def fetch_data(self) -> AsyncGenerator[RawData, None]:
        """Fetch market data for correlation analysis"""
        async for data in self._generate_mock_financial():
            yield data
    
    async def _generate_mock_financial(self) -> AsyncGenerator[RawData, None]:
        """Generate mock financial data"""
        import random
        symbols = data_config.CRYPTO_SYMBOLS + data_config.STOCK_SYMBOLS
        
        while self.is_running:
            symbol = random.choice(symbols)
            price = random.uniform(100, 50000)
            change = random.uniform(-0.15, 0.15)
            volume = random.uniform(1000000, 100000000)
            
            financial_data = {
                "symbol": symbol,
                "price": price,
                "change_24h": change,
                "volume": volume,
                "timestamp": datetime.now().isoformat()
            }
            
            data = RawData(
                id=f"market_{symbol}_{datetime.now().timestamp()}",
                source=self.source,
                timestamp=datetime.now(),
                content=json.dumps(financial_data),
                metadata={"symbol": symbol, "data_type": "market_data"}
            )
            yield data
            await asyncio.sleep(random.uniform(5, 15))

class DataIngestionManager:
    """Manages multiple data ingestion sources"""
    
    def __init__(self):
        self.sources = {
            DataSource.TWITTER: TwitterIngestion(),
            DataSource.REDDIT: RedditIngestion(),
            DataSource.NEWS: NewsIngestion(),
            DataSource.FINANCIAL: FinancialDataIngestion()
        }
        self.is_running = False
        self.tasks = []
    
    async def start_all(self):
        """Start all data ingestion sources"""
        self.is_running = True
        for source in self.sources.values():
            await source.start()
            task = asyncio.create_task(self._process_source_data(source))
            self.tasks.append(task)
        logger.info("All data ingestion sources started")
    
    async def stop_all(self):
        """Stop all data ingestion sources"""
        self.is_running = False
        for task in self.tasks:
            task.cancel()
        for source in self.sources.values():
            await source.stop()
        logger.info("All data ingestion sources stopped")
    
    async def _process_source_data(self, source: DataIngestionBase):
        """Process data from a specific source"""
        try:
            async for data in source.fetch_data():
                if not self.is_running:
                    break
                # Here we would normally send data to sentiment analysis pipeline
                logger.debug(f"Received data from {source.source.value}: {data.content[:100]}...")
        except asyncio.CancelledError:
            logger.info(f"Data processing cancelled for {source.source.value}")
        except Exception as e:
            logger.error(f"Error processing data from {source.source.value}: {e}")