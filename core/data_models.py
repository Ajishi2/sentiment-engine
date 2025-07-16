"""
Core data models for the sentiment engine
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

class SentimentPolarity(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class DataSource(Enum):
    TWITTER = "TWITTER"
    REDDIT = "REDDIT"
    NEWS = "NEWS"
    FINANCIAL = "FINANCIAL"

@dataclass
class RawData:
    """Raw data from various sources"""
    id: str
    source: DataSource
    timestamp: datetime
    content: str
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SentimentScore:
    """Sentiment analysis result"""
    polarity: SentimentPolarity
    confidence: float
    score: float  # -1.0 to 1.0
    emotions: Dict[str, float] = field(default_factory=dict)
    entities: List[str] = field(default_factory=list)

@dataclass
class ProcessedData:
    """Processed data with sentiment analysis"""
    raw_data: RawData
    sentiment: SentimentScore
    financial_entities: List[str] = field(default_factory=list)
    relevance_score: float = 0.0
    language: str = "en"

@dataclass
class AggregatedSentiment:
    """Aggregated sentiment for a specific asset/timeframe"""
    asset: str
    timestamp: datetime
    window_size: int  # seconds
    total_mentions: int
    sentiment_score: float
    confidence: float
    volume_weighted_score: float
    momentum: float
    sources_breakdown: Dict[DataSource, Dict[str, float]]

@dataclass
class MarketData:
    """Market data for correlation analysis"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    change_24h: float
    market_cap: Optional[float] = None
    additional_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class FearGreedIndex:
    """Fear & Greed Index calculation"""
    timestamp: datetime
    overall_score: float  # 0-100
    sentiment_component: float
    momentum_component: float
    volume_component: float
    correlation_component: float
    classification: str  # "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"

@dataclass
class TradingSignal:
    """Trading signal with confidence and risk metrics"""
    asset: str
    timestamp: datetime
    signal_type: SignalType
    confidence: float
    strength: float  # 0-1
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    position_size: float = 0.0
    reasoning: str = ""
    supporting_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CorrelationAnalysis:
    """Correlation analysis between sentiment and price movements"""
    asset: str
    timeframe: str
    sentiment_price_correlation: float
    sentiment_volume_correlation: float
    predictive_power: float
    statistical_significance: float
    sample_size: int

@dataclass
class BacktestResult:
    """Backtesting performance result"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: float
    details: Dict[str, Any] = field(default_factory=dict)