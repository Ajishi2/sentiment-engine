"""
API Setup Guide and Testing Script
"""
import asyncio
import logging
from datetime import datetime

from api_integrations.twitter_client import TwitterAPIClient, DEFAULT_TWITTER_RULES
from api_integrations.reddit_client import RedditAPIClient
from api_integrations.news_client import NewsAPIClient, AlphaVantageNewsClient
from api_integrations.financial_data_client import FinancialDataClient
from database.supabase_client import db_client
from config import api_config, data_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APISetupGuide:
    """Guide for setting up all required APIs"""
    
    def __init__(self):
        self.apis_status = {}
    
    async def test_all_apis(self):
        """Test all API connections and functionality"""
        logger.info("=" * 60)
        logger.info("FEAR & GREED SENTIMENT ENGINE - API SETUP GUIDE")
        logger.info("=" * 60)
        
        # Test Supabase
        await self._test_supabase()
        
        # Test Twitter API
        await self._test_twitter_api()
        
        # Test Reddit API
        await self._test_reddit_api()
        
        # Test News APIs
        await self._test_news_apis()
        
        # Test Financial Data APIs
        await self._test_financial_apis()
        
        # Print summary
        self._print_setup_summary()
    
    async def _test_supabase(self):
        """Test Supabase connection"""
        logger.info("\n🗄️  TESTING SUPABASE DATABASE")
        logger.info("-" * 40)
        
        try:
            if db_client.is_connected:
                logger.info("✅ Supabase connection: SUCCESS")
                await db_client.create_tables()
                logger.info("✅ Database tables: VERIFIED")
                self.apis_status['supabase'] = 'connected'
            else:
                logger.warning("⚠️  Supabase connection: NOT CONFIGURED")
                logger.info("   Using mock storage for demo purposes")
                self.apis_status['supabase'] = 'mock'
                
        except Exception as e:
            logger.error(f"❌ Supabase error: {e}")
            self.apis_status['supabase'] = 'error'
    
    async def _test_twitter_api(self):
        """Test Twitter API connection"""
        logger.info("\n🐦 TESTING TWITTER API")
        logger.info("-" * 40)
        
        try:
            client = TwitterAPIClient()
            
            if api_config.TWITTER_BEARER_TOKEN == 'demo_token':
                logger.warning("⚠️  Twitter API: DEMO MODE")
                logger.info("   Using mock Twitter data")
                logger.info("   To use real Twitter data:")
                logger.info("   1. Get Twitter API v2 Bearer Token from https://developer.twitter.com")
                logger.info("   2. Set TWITTER_BEARER_TOKEN in .env file")
                self.apis_status['twitter'] = 'demo'
            else:
                # Test real API
                tweets = await client.search_recent_tweets("bitcoin", max_results=5)
                logger.info(f"✅ Twitter API: SUCCESS ({len(tweets)} tweets fetched)")
                self.apis_status['twitter'] = 'connected'
                
        except Exception as e:
            logger.error(f"❌ Twitter API error: {e}")
            self.apis_status['twitter'] = 'error'
        finally:
            await client.close_session()
    
    async def _test_reddit_api(self):
        """Test Reddit API connection"""
        logger.info("\n🔴 TESTING REDDIT API")
        logger.info("-" * 40)
        
        try:
            client = RedditAPIClient()
            
            if api_config.REDDIT_CLIENT_ID == 'demo_client':
                logger.warning("⚠️  Reddit API: DEMO MODE")
                logger.info("   Using mock Reddit data")
                logger.info("   To use real Reddit data:")
                logger.info("   1. Create Reddit app at https://www.reddit.com/prefs/apps")
                logger.info("   2. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
                self.apis_status['reddit'] = 'demo'
            else:
                # Test real API
                posts = await client.get_subreddit_posts('cryptocurrency', limit=5)
                logger.info(f"✅ Reddit API: SUCCESS ({len(posts)} posts fetched)")
                self.apis_status['reddit'] = 'connected'
                
        except Exception as e:
            logger.error(f"❌ Reddit API error: {e}")
            self.apis_status['reddit'] = 'error'
        finally:
            await client.close_session()
    
    async def _test_news_apis(self):
        """Test News API connections"""
        logger.info("\n📰 TESTING NEWS APIs")
        logger.info("-" * 40)
        
        # Test NewsAPI
        try:
            client = NewsAPIClient()
            
            if api_config.NEWS_API_KEY == 'demo_key':
                logger.warning("⚠️  NewsAPI: DEMO MODE")
                logger.info("   Using mock news data")
                logger.info("   To use real NewsAPI:")
                logger.info("   1. Get free API key from https://newsapi.org")
                logger.info("   2. Set NEWS_API_KEY in .env file")
                self.apis_status['newsapi'] = 'demo'
            else:
                # Test real API
                news = await client.get_financial_news(page_size=5)
                logger.info(f"✅ NewsAPI: SUCCESS ({len(news)} articles fetched)")
                self.apis_status['newsapi'] = 'connected'
                
        except Exception as e:
            logger.error(f"❌ NewsAPI error: {e}")
            self.apis_status['newsapi'] = 'error'
        finally:
            await client.close_session()
        
        # Test Alpha Vantage News
        try:
            client = AlphaVantageNewsClient()
            
            if api_config.ALPHA_VANTAGE_KEY == 'demo_key':
                logger.warning("⚠️  Alpha Vantage: DEMO MODE")
                logger.info("   To use Alpha Vantage:")
                logger.info("   1. Get free API key from https://www.alphavantage.co")
                logger.info("   2. Set ALPHA_VANTAGE_KEY in .env file")
                self.apis_status['alphavantage'] = 'demo'
            else:
                # Test real API
                news = await client.get_news_sentiment(limit=5)
                logger.info(f"✅ Alpha Vantage: SUCCESS ({len(news)} articles fetched)")
                self.apis_status['alphavantage'] = 'connected'
                
        except Exception as e:
            logger.error(f"❌ Alpha Vantage error: {e}")
            self.apis_status['alphavantage'] = 'error'
        finally:
            await client.close_session()
    
    async def _test_financial_apis(self):
        """Test Financial Data APIs"""
        logger.info("\n💹 TESTING FINANCIAL DATA APIs")
        logger.info("-" * 40)
        
        try:
            client = FinancialDataClient()
            
            # Test Yahoo Finance (free)
            stock_data = await client.get_stock_data(['AAPL'])
            logger.info(f"✅ Yahoo Finance: SUCCESS ({len(stock_data)} stocks)")
            
            # Test CoinGecko (free)
            crypto_data = await client.get_crypto_data(['BTC', 'ETH'])
            logger.info(f"✅ CoinGecko: SUCCESS ({len(crypto_data)} cryptos)")
            
            self.apis_status['financial'] = 'connected'
            
        except Exception as e:
            logger.error(f"❌ Financial APIs error: {e}")
            self.apis_status['financial'] = 'error'
        finally:
            await client.close_session()
    
    def _print_setup_summary(self):
        """Print setup summary and next steps"""
        logger.info("\n" + "=" * 60)
        logger.info("API SETUP SUMMARY")
        logger.info("=" * 60)
        
        for api, status in self.apis_status.items():
            if status == 'connected':
                logger.info(f"✅ {api.upper()}: CONNECTED")
            elif status == 'demo':
                logger.info(f"⚠️  {api.upper()}: DEMO MODE")
            else:
                logger.info(f"❌ {api.upper()}: ERROR")
        
        logger.info("\n📋 NEXT STEPS:")
        logger.info("1. Copy .env.example to .env")
        logger.info("2. Add your API keys to the .env file")
        logger.info("3. Run 'python run_demo.py' to start the demo")
        logger.info("4. Run 'python dashboard/app.py' for the web dashboard")
        
        logger.info("\n🔗 API REGISTRATION LINKS:")
        logger.info("• Twitter API: https://developer.twitter.com")
        logger.info("• Reddit API: https://www.reddit.com/prefs/apps")
        logger.info("• NewsAPI: https://newsapi.org")
        logger.info("• Alpha Vantage: https://www.alphavantage.co")
        logger.info("• Supabase: https://supabase.com")
        
        logger.info("\n💡 FREE TIER LIMITS:")
        logger.info("• Twitter API v2: 500K tweets/month")
        logger.info("• Reddit API: 60 requests/minute")
        logger.info("• NewsAPI: 1000 requests/day")
        logger.info("• Alpha Vantage: 5 calls/minute")
        logger.info("• CoinGecko: 50 calls/minute")
        logger.info("• Yahoo Finance: Unlimited (via yfinance)")

async def main():
    """Run API setup and testing"""
    setup_guide = APISetupGuide()
    await setup_guide.test_all_apis()

if __name__ == "__main__":
    asyncio.run(main())