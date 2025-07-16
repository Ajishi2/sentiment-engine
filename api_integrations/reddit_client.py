"""
Reddit API integration for sentiment analysis
"""
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict, Optional, AsyncGenerator
import base64

from config import api_config, data_config
from core.data_models import RawData, DataSource

logger = logging.getLogger(__name__)

class RedditAPIClient:
    """Reddit API client for sentiment data collection"""
    
    def __init__(self):
        self.client_id = api_config.REDDIT_CLIENT_ID
        self.client_secret = api_config.REDDIT_CLIENT_SECRET
        self.user_agent = api_config.REDDIT_USER_AGENT
        self.base_url = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        
    async def start_session(self):
        """Start HTTP session and authenticate"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        if self.client_id != 'demo_client':
            await self._authenticate()
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _authenticate(self):
        """Authenticate with Reddit API"""
        try:
            # Prepare authentication
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': self.user_agent
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            async with self.session.post(self.auth_url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    logger.info("Reddit API authentication successful")
                else:
                    logger.error(f"Reddit authentication failed: {response.status}")
        except Exception as e:
            logger.error(f"Error authenticating with Reddit: {e}")
    
    async def get_subreddit_posts(self, subreddit: str, sort: str = 'hot', 
                                 limit: int = 100, time_filter: str = 'day') -> List[RawData]:
        """Get posts from a specific subreddit"""
        if self.client_id == 'demo_client':
            return await self._generate_mock_posts(limit)
        
        await self.start_session()
        
        try:
            url = f"{self.base_url}/r/{subreddit}/{sort}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent
            }
            
            params = {
                'limit': min(limit, 100),
                't': time_filter
            }
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_reddit_posts(data, subreddit)
                else:
                    logger.error(f"Reddit API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Reddit posts: {e}")
            return []
    
    async def get_post_comments(self, subreddit: str, post_id: str, 
                               limit: int = 50) -> List[RawData]:
        """Get comments from a specific post"""
        if self.client_id == 'demo_client':
            return await self._generate_mock_comments(limit)
        
        await self.start_session()
        
        try:
            url = f"{self.base_url}/r/{subreddit}/comments/{post_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent
            }
            
            params = {'limit': limit}
            
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_reddit_comments(data, subreddit)
                else:
                    logger.error(f"Reddit comments API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Reddit comments: {e}")
            return []
    
    async def stream_subreddit_data(self, subreddits: List[str]) -> AsyncGenerator[RawData, None]:
        """Stream data from multiple subreddits"""
        while True:
            try:
                for subreddit in subreddits:
                    posts = await self.get_subreddit_posts(subreddit, limit=10)
                    for post in posts:
                        yield post
                    
                    # Get some comments from recent posts
                    if posts:
                        recent_post = posts[0]
                        post_id = recent_post.metadata.get('post_id')
                        if post_id:
                            comments = await self.get_post_comments(subreddit, post_id, limit=5)
                            for comment in comments:
                                yield comment
                
                # Wait before next fetch
                await asyncio.sleep(300)  # 5 minutes between fetches
                
            except Exception as e:
                logger.error(f"Error in Reddit stream: {e}")
                await asyncio.sleep(60)
    
    def _parse_reddit_posts(self, data: Dict, subreddit: str) -> List[RawData]:
        """Parse Reddit API response for posts"""
        raw_data_list = []
        
        try:
            posts = data['data']['children']
            
            for post_data in posts:
                post = post_data['data']
                
                # Skip removed or deleted posts
                if post.get('removed_by_category') or post.get('selftext') == '[deleted]':
                    continue
                
                # Combine title and selftext
                content = post['title']
                if post.get('selftext'):
                    content += f" {post['selftext']}"
                
                # Parse timestamp
                timestamp = datetime.fromtimestamp(post['created_utc'])
                
                raw_data = RawData(
                    id=f"reddit_post_{post['id']}",
                    source=DataSource.REDDIT,
                    timestamp=timestamp,
                    content=content,
                    author=post.get('author', 'unknown'),
                    metadata={
                        'subreddit': subreddit,
                        'post_id': post['id'],
                        'score': post.get('score', 0),
                        'upvote_ratio': post.get('upvote_ratio', 0.5),
                        'num_comments': post.get('num_comments', 0),
                        'url': post.get('url', ''),
                        'flair': post.get('link_flair_text', ''),
                        'post_type': 'post'
                    }
                )
                
                raw_data_list.append(raw_data)
                
        except Exception as e:
            logger.error(f"Error parsing Reddit posts: {e}")
        
        return raw_data_list
    
    def _parse_reddit_comments(self, data: List, subreddit: str) -> List[RawData]:
        """Parse Reddit API response for comments"""
        raw_data_list = []
        
        try:
            # Comments are in the second element of the response
            if len(data) > 1:
                comments = data[1]['data']['children']
                
                for comment_data in comments:
                    if comment_data['kind'] != 't1':  # Skip non-comment items
                        continue
                    
                    comment = comment_data['data']
                    
                    # Skip removed or deleted comments
                    if comment.get('body') in ['[deleted]', '[removed]']:
                        continue
                    
                    # Parse timestamp
                    timestamp = datetime.fromtimestamp(comment['created_utc'])
                    
                    raw_data = RawData(
                        id=f"reddit_comment_{comment['id']}",
                        source=DataSource.REDDIT,
                        timestamp=timestamp,
                        content=comment['body'],
                        author=comment.get('author', 'unknown'),
                        metadata={
                            'subreddit': subreddit,
                            'comment_id': comment['id'],
                            'score': comment.get('score', 0),
                            'parent_id': comment.get('parent_id', ''),
                            'post_type': 'comment'
                        }
                    )
                    
                    raw_data_list.append(raw_data)
                    
        except Exception as e:
            logger.error(f"Error parsing Reddit comments: {e}")
        
        return raw_data_list
    
    async def _generate_mock_posts(self, count: int) -> List[RawData]:
        """Generate mock Reddit posts for demo"""
        mock_posts = [
            "Just bought more BTC during this dip. Diamond hands! 💎🙌",
            "Technical analysis suggests we're entering a bear market. Thoughts?",
            "DCA strategy has been working great for me. Down 20% but still buying",
            "FOMO is real right now. Should I wait for a better entry point?",
            "TA suggests we might see $100k Bitcoin soon. What do you think?",
            "Panic selling everywhere. This is when you separate weak from strong hands",
            "Institutional adoption is accelerating. Very bullish long term",
            "Market manipulation is obvious. Whales dumping to cause fear",
            "Best time to accumulate is when everyone else is fearful",
            "This volatility is exactly why crypto isn't for everyone"
        ]
        
        import random
        posts = []
        for i in range(count):
            post_text = random.choice(mock_posts)
            posts.append(RawData(
                id=f"mock_reddit_post_{datetime.now().timestamp()}_{i}",
                source=DataSource.REDDIT,
                timestamp=datetime.now(),
                content=post_text,
                author=f"redditor_{random.randint(1000, 9999)}",
                metadata={
                    'subreddit': random.choice(data_config.REDDIT_SUBREDDITS),
                    'score': random.randint(-10, 100),
                    'upvote_ratio': random.uniform(0.5, 0.95),
                    'num_comments': random.randint(0, 50),
                    'post_type': 'post'
                }
            ))
        
        return posts
    
    async def _generate_mock_comments(self, count: int) -> List[RawData]:
        """Generate mock Reddit comments for demo"""
        mock_comments = [
            "This is exactly what I've been saying for months",
            "Thanks for sharing this analysis, very helpful",
            "I disagree, the fundamentals are still strong",
            "RemindMe! 6 months",
            "Source? This sounds like speculation",
            "Finally someone who gets it",
            "This aged well... NOT",
            "Buy high sell low, the reddit way",
            "HODL gang where you at?",
            "Time in the market beats timing the market"
        ]
        
        import random
        comments = []
        for i in range(count):
            comment_text = random.choice(mock_comments)
            comments.append(RawData(
                id=f"mock_reddit_comment_{datetime.now().timestamp()}_{i}",
                source=DataSource.REDDIT,
                timestamp=datetime.now(),
                content=comment_text,
                author=f"commenter_{random.randint(1000, 9999)}",
                metadata={
                    'subreddit': random.choice(data_config.REDDIT_SUBREDDITS),
                    'score': random.randint(-5, 25),
                    'post_type': 'comment'
                }
            ))
        
        return comments