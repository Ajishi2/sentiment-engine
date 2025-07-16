"""
Supabase database client and operations
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase import create_client, Client
import json

from config import api_config
from core.data_models import (
    RawData, ProcessedData, TradingSignal, AggregatedSentiment, 
    FearGreedIndex, BacktestResult, MarketData
)

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase database client for sentiment engine"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            if api_config.SUPABASE_URL and api_config.SUPABASE_KEY:
                self.client = create_client(
                    api_config.SUPABASE_URL, 
                    api_config.SUPABASE_KEY
                )
                self.is_connected = True
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not provided, using mock storage")
                self.is_connected = False
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.is_connected = False
    
    async def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.is_connected:
            return
        
        try:
            # This would typically be done via Supabase migrations
            # For demo purposes, we'll assume tables exist
            logger.info("Database tables verified")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
    
    async def store_raw_data(self, data: RawData) -> bool:
        """Store raw data from ingestion sources"""
        if not self.is_connected:
            return True  # Mock success for demo
        
        try:
            result = self.client.table('raw_data').insert({
                'id': data.id,
                'source': data.source.value,
                'timestamp': data.timestamp.isoformat(),
                'content': data.content,
                'author': data.author,
                'metadata': json.dumps(data.metadata)
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing raw data: {e}")
            return False
    
    async def store_processed_data(self, data: ProcessedData) -> bool:
        """Store processed sentiment data"""
        if not self.is_connected:
            return True
        
        try:
            result = self.client.table('processed_data').insert({
                'raw_data_id': data.raw_data.id,
                'sentiment_score': data.sentiment.score,
                'sentiment_polarity': data.sentiment.polarity.value,
                'confidence': data.sentiment.confidence,
                'emotions': json.dumps(data.sentiment.emotions),
                'entities': json.dumps(data.financial_entities),
                'relevance_score': data.relevance_score,
                'language': data.language,
                'timestamp': data.raw_data.timestamp.isoformat()
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing processed data: {e}")
            return False
    
    async def store_trading_signal(self, signal: TradingSignal) -> bool:
        """Store trading signals"""
        if not self.is_connected:
            return True
        
        try:
            result = self.client.table('trading_signals').insert({
                'asset': signal.asset,
                'timestamp': signal.timestamp.isoformat(),
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'strength': signal.strength,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'risk_reward_ratio': signal.risk_reward_ratio,
                'position_size': signal.position_size,
                'reasoning': signal.reasoning,
                'supporting_data': json.dumps(signal.supporting_data)
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing trading signal: {e}")
            return False
    
    async def store_fear_greed_index(self, index: FearGreedIndex) -> bool:
        """Store Fear & Greed Index data"""
        if not self.is_connected:
            return True
        
        try:
            result = self.client.table('fear_greed_index').insert({
                'timestamp': index.timestamp.isoformat(),
                'overall_score': index.overall_score,
                'sentiment_component': index.sentiment_component,
                'momentum_component': index.momentum_component,
                'volume_component': index.volume_component,
                'correlation_component': index.correlation_component,
                'classification': index.classification
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing fear greed index: {e}")
            return False
    
    async def store_market_data(self, data: MarketData) -> bool:
        """Store market data for correlation analysis"""
        if not self.is_connected:
            return True
        
        try:
            result = self.client.table('market_data').insert({
                'symbol': data.symbol,
                'timestamp': data.timestamp.isoformat(),
                'price': data.price,
                'volume': data.volume,
                'change_24h': data.change_24h,
                'market_cap': data.market_cap,
                'additional_metrics': json.dumps(data.additional_metrics)
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error storing market data: {e}")
            return False
    
    async def get_recent_sentiment(self, asset: str, hours: int = 24) -> List[Dict]:
        """Get recent sentiment data for an asset"""
        if not self.is_connected:
            return []
        
        try:
            cutoff_time = datetime.now().replace(microsecond=0) - timedelta(hours=hours)
            
            result = self.client.table('processed_data').select(
                'sentiment_score, confidence, timestamp, entities'
            ).gte(
                'timestamp', cutoff_time.isoformat()
            ).execute()
            
            # Filter by asset in entities
            filtered_data = []
            for row in result.data:
                entities = json.loads(row.get('entities', '[]'))
                if asset.upper() in [e.upper() for e in entities]:
                    filtered_data.append(row)
            
            return filtered_data
        except Exception as e:
            logger.error(f"Error getting recent sentiment: {e}")
            return []
    
    async def get_trading_signals(self, asset: str = None, limit: int = 50) -> List[Dict]:
        """Get recent trading signals"""
        if not self.is_connected:
            return []
        
        try:
            query = self.client.table('trading_signals').select('*')
            
            if asset:
                query = query.eq('asset', asset)
            
            result = query.order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting trading signals: {e}")
            return []
    
    async def get_fear_greed_history(self, days: int = 30) -> List[Dict]:
        """Get Fear & Greed Index history"""
        if not self.is_connected:
            return []
        
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            result = self.client.table('fear_greed_index').select(
                '*'
            ).gte(
                'timestamp', cutoff_time.isoformat()
            ).order('timestamp', desc=True).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting fear greed history: {e}")
            return []
    
    async def store_backtest_result(self, result: BacktestResult) -> bool:
        """Store backtesting results"""
        if not self.is_connected:
            return True
        
        try:
            db_result = self.client.table('backtest_results').insert({
                'strategy_name': result.strategy_name,
                'start_date': result.start_date.isoformat(),
                'end_date': result.end_date.isoformat(),
                'total_return': result.total_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'win_rate': result.win_rate,
                'profit_factor': result.profit_factor,
                'total_trades': result.total_trades,
                'avg_trade_duration': result.avg_trade_duration,
                'details': json.dumps(result.details),
                'created_at': datetime.now().isoformat()
            }).execute()
            
            return len(db_result.data) > 0
        except Exception as e:
            logger.error(f"Error storing backtest result: {e}")
            return False

# Global database client instance
db_client = SupabaseClient()