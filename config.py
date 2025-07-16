"""
Configuration settings for the Fear & Greed Sentiment Engine
"""
import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

@dataclass
class APIConfig:
    """API configuration settings"""
    # Social Media APIs (use environment variables for production)
    TWITTER_BEARER_TOKEN: str = os.getenv('TWITTER_BEARER_TOKEN', 'demo_token')
    REDDIT_CLIENT_ID: str = os.getenv('REDDIT_CLIENT_ID', 'demo_client')
    REDDIT_CLIENT_SECRET: str = os.getenv('REDDIT_CLIENT_SECRET', 'demo_secret')
    REDDIT_USER_AGENT: str = os.getenv('REDDIT_USER_AGENT', 'SentimentBot/1.0')
    
    # News APIs
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', 'demo_key')
    
    # Financial Data APIs
    ALPHA_VANTAGE_KEY: str = os.getenv('ALPHA_VANTAGE_KEY', 'demo_key')
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY: str = os.getenv('SUPABASE_ANON_KEY', '')
    
    # Hugging Face (for advanced models)
    HUGGINGFACE_TOKEN: str = os.getenv('HUGGINGFACE_TOKEN', '')

@dataclass
class ProcessingConfig:
    """Data processing configuration"""
    # Sentiment Analysis
    SENTIMENT_MODEL: str = "nlptown/bert-base-multilingual-uncased-sentiment"
    FINANCIAL_MODEL: str = "ProsusAI/finbert"
    
    # Processing Parameters
    MAX_TEXT_LENGTH: int = 512
    BATCH_SIZE: int = 32
    SENTIMENT_THRESHOLD: float = 0.6
    
    # Time Windows
    REAL_TIME_WINDOW: int = 60  # seconds
    SHORT_TERM_WINDOW: int = 300  # 5 minutes
    MEDIUM_TERM_WINDOW: int = 3600  # 1 hour
    LONG_TERM_WINDOW: int = 86400  # 1 day

@dataclass
class TradingConfig:
    """Trading signal configuration"""
    # Fear & Greed Index Thresholds
    EXTREME_FEAR_THRESHOLD: float = 25
    FEAR_THRESHOLD: float = 45
    NEUTRAL_THRESHOLD: float = 55
    GREED_THRESHOLD: float = 75
    EXTREME_GREED_THRESHOLD: float = 90
    
    # Signal Generation
    MIN_SIGNAL_CONFIDENCE: float = 0.7
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    STOP_LOSS_PERCENTAGE: float = 0.05  # 5%
    TAKE_PROFIT_PERCENTAGE: float = 0.15  # 15%
    
    # Risk Management
    MAX_DAILY_LOSS: float = 0.02  # 2%
    MAX_CORRELATION_EXPOSURE: float = 0.3  # 30%

@dataclass
class DataConfig:
    """Data sources and targets configuration"""
    # Supported Assets
    CRYPTO_SYMBOLS: List[str] = None
    STOCK_SYMBOLS: List[str] = None
    
    # Social Media Sources
    TWITTER_KEYWORDS: List[str] = None
    REDDIT_SUBREDDITS: List[str] = None
    
    # News Sources
    NEWS_SOURCES: List[str] = None
    
    def __post_init__(self):
        if self.CRYPTO_SYMBOLS is None:
            self.CRYPTO_SYMBOLS = ['BTC', 'ETH', 'ADA', 'SOL', 'MATIC', 'DOGE', 'XRP']
        
        if self.STOCK_SYMBOLS is None:
            self.STOCK_SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']
        
        if self.TWITTER_KEYWORDS is None:
            self.TWITTER_KEYWORDS = [
                'bitcoin', 'crypto', 'blockchain', 'defi', 'nft',
                'stocks', 'trading', 'investing', 'market', 'bull', 'bear'
            ]
        
        if self.REDDIT_SUBREDDITS is None:
            self.REDDIT_SUBREDDITS = [
                'cryptocurrency', 'bitcoin', 'investing', 'stocks', 
                'wallstreetbets', 'ethfinance', 'defi'
            ]
        
        if self.NEWS_SOURCES is None:
            self.NEWS_SOURCES = [
                'reuters', 'bloomberg', 'cnbc', 'marketwatch', 
                'coindesk', 'cointelegraph', 'decrypt'
            ]

# Global configuration instances
api_config = APIConfig()
processing_config = ProcessingConfig()
trading_config = TradingConfig()
data_config = DataConfig()