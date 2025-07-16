"""
Twitter API v2 integration for real-time sentiment data
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import AsyncGenerator, List, Dict, Optional
import json

from config import api_config, data_config
from core.data_models import RawData, DataSource

logger = logging.getLogger(__name__)

class TwitterAPIClient:
    """Twitter API v2 client for real-time data streaming"""
    
    def __init__(self):
        self.bearer_token = api_config.TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_streaming = False
        
    async def start_session(self):
        """Start HTTP session"""
        if not self.session:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_recent_tweets(self, query: str, max_results: int = 100) -> List[RawData]:
        """Search for recent tweets matching query"""
        if self.bearer_token == 'demo_token':
            return await self._generate_mock_tweets(max_results)
        
        await self.start_session()
        
        try:
            url = f"{self.base_url}/tweets/search/recent"
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations",
                "expansions": "author_id",
                "user.fields": "username,verified,public_metrics"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_twitter_response(data)
                else:
                    logger.error(f"Twitter API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []
    
    async def stream_filtered_tweets(self, rules: List[Dict]) -> AsyncGenerator[RawData, None]:
        """Stream tweets using filtered stream endpoint"""
        if self.bearer_token == 'demo_token':
            async for tweet in self._stream_mock_tweets():
                yield tweet
            return
        
        await self.start_session()
        
        try:
            # Add rules to the stream
            await self._add_stream_rules(rules)
            
            # Start streaming
            url = f"{self.base_url}/tweets/search/stream"
            params = {
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations",
                "expansions": "author_id",
                "user.fields": "username,verified,public_metrics"
            }
            
            self.is_streaming = True
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    async for line in response.content:
                        if not self.is_streaming:
                            break
                        
                        if line:
                            try:
                                tweet_data = json.loads(line.decode('utf-8'))
                                if 'data' in tweet_data:
                                    raw_data = self._parse_single_tweet(tweet_data)
                                    if raw_data:
                                        yield raw_data
                            except json.JSONDecodeError:
                                continue
                else:
                    logger.error(f"Twitter stream error: {response.status}")
        except Exception as e:
            logger.error(f"Error in Twitter stream: {e}")
        finally:
            self.is_streaming = False
    
    async def _add_stream_rules(self, rules: List[Dict]):
        """Add rules to Twitter filtered stream"""
        url = f"{self.base_url}/tweets/search/stream/rules"
        
        # Get existing rules
        async with self.session.get(url) as response:
            if response.status == 200:
                existing_rules = await response.json()
                
                # Delete existing rules if any
                if existing_rules.get('data'):
                    rule_ids = [rule['id'] for rule in existing_rules['data']]
                    delete_payload = {"delete": {"ids": rule_ids}}
                    await self.session.post(url, json=delete_payload)
        
        # Add new rules
        add_payload = {"add": rules}
        async with self.session.post(url, json=add_payload) as response:
            if response.status == 201:
                logger.info("Twitter stream rules added successfully")
            else:
                logger.error(f"Failed to add stream rules: {response.status}")
    
    def _parse_twitter_response(self, data: Dict) -> List[RawData]:
        """Parse Twitter API response into RawData objects"""
        raw_data_list = []
        
        tweets = data.get('data', [])
        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
        
        for tweet in tweets:
            raw_data = self._parse_single_tweet({'data': tweet}, users)
            if raw_data:
                raw_data_list.append(raw_data)
        
        return raw_data_list
    
    def _parse_single_tweet(self, tweet_data: Dict, users: Dict = None) -> Optional[RawData]:
        """Parse a single tweet into RawData"""
        try:
            tweet = tweet_data['data']
            author_id = tweet.get('author_id')
            
            # Get user info if available
            author_username = None
            if users and author_id in users:
                author_username = users[author_id].get('username')
            
            # Parse timestamp
            created_at = tweet.get('created_at')
            if created_at:
                timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            # Extract metrics
            metrics = tweet.get('public_metrics', {})
            
            return RawData(
                id=f"twitter_{tweet['id']}",
                source=DataSource.TWITTER,
                timestamp=timestamp,
                content=tweet['text'],
                author=author_username or author_id,
                metadata={
                    'retweet_count': metrics.get('retweet_count', 0),
                    'like_count': metrics.get('like_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0),
                    'context_annotations': tweet.get('context_annotations', [])
                }
            )
        except Exception as e:
            logger.error(f"Error parsing tweet: {e}")
            return None
    
    async def _generate_mock_tweets(self, count: int) -> List[RawData]:
        """Generate mock tweets for demo purposes"""
        mock_tweets = [
            "Bitcoin is absolutely mooning right now! 🚀 This bull run is just getting started #BTC #crypto",
            "Major selloff in crypto markets today. Perfect time to buy the dip? 🤔 #Bitcoin #ETH",
            "BREAKING: Another major institution announces Bitcoin allocation 📈 #crypto #news",
            "Market looking very bearish right now. Time to be cautious with positions 📉 #stocks #trading",
            "Ethereum hitting new highs! DeFi season is definitely here 🌟 #ETH #DeFi",
            "So much FUD spreading everywhere but fundamentals remain strong 💪 #HODL",
            "This volatility is absolutely insane! Markets going crazy today 📊 #trading",
            "Accumulating more during this dip. Long term I'm still very bullish 📈 #investing",
            "Fear and greed index showing extreme fear. Usually a good contrarian signal 📊",
            "Technical analysis suggests we might see $100k Bitcoin soon 🎯 #BTC #TA"
        ]
        
        import random
        tweets = []
        for i in range(count):
            tweet_text = random.choice(mock_tweets)
            tweets.append(RawData(
                id=f"mock_twitter_{datetime.now().timestamp()}_{i}",
                source=DataSource.TWITTER,
                timestamp=datetime.now(),
                content=tweet_text,
                author=f"user_{random.randint(1000, 9999)}",
                metadata={
                    'retweet_count': random.randint(0, 100),
                    'like_count': random.randint(0, 500),
                    'reply_count': random.randint(0, 50),
                    'quote_count': random.randint(0, 20)
                }
            ))
        
        return tweets
    
    async def _stream_mock_tweets(self) -> AsyncGenerator[RawData, None]:
        """Stream mock tweets for demo"""
        while self.is_streaming:
            tweets = await self._generate_mock_tweets(1)
            if tweets:
                yield tweets[0]
            await asyncio.sleep(random.uniform(2, 8))
    
    def stop_streaming(self):
        """Stop the streaming process"""
        self.is_streaming = False

# Create default Twitter stream rules for financial content
DEFAULT_TWITTER_RULES = [
    {
        "value": "(bitcoin OR BTC OR cryptocurrency OR crypto) lang:en -is:retweet",
        "tag": "crypto_sentiment"
    },
    {
        "value": "(ethereum OR ETH OR DeFi) lang:en -is:retweet",
        "tag": "ethereum_sentiment"
    },
    {
        "value": "(stocks OR trading OR investing OR market) lang:en -is:retweet",
        "tag": "market_sentiment"
    },
    {
        "value": "(bull OR bear OR pump OR dump OR moon) lang:en -is:retweet",
        "tag": "sentiment_keywords"
    }
]