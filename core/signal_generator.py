"""
Trading signal generation based on sentiment analysis
"""
import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import json

from config import trading_config, processing_config
from core.data_models import (
    ProcessedData, AggregatedSentiment, TradingSignal, SignalType,
    FearGreedIndex, MarketData, CorrelationAnalysis
)

logger = logging.getLogger(__name__)

class SentimentAggregator:
    """Aggregate sentiment data across different timeframes"""
    
    def __init__(self):
        self.sentiment_data = defaultdict(lambda: deque(maxlen=1000))
        self.aggregated_cache = {}
        
    def add_sentiment_data(self, data: ProcessedData):
        """Add processed sentiment data"""
        # Extract asset from entities or content
        assets = self._extract_assets(data)
        
        for asset in assets:
            self.sentiment_data[asset].append({
                'timestamp': data.raw_data.timestamp,
                'sentiment_score': data.sentiment.score,
                'confidence': data.sentiment.confidence,
                'relevance': data.relevance_score,
                'source': data.raw_data.source,
                'volume_proxy': self._calculate_volume_proxy(data)
            })
    
    def _extract_assets(self, data: ProcessedData) -> List[str]:
        """Extract asset symbols from processed data"""
        assets = []
        
        # From entities
        for entity in data.financial_entities:
            normalized = self._normalize_asset_name(entity)
            if normalized:
                assets.append(normalized)
        
        # If no specific assets found, add to general market sentiment
        if not assets:
            assets.append('MARKET')
        
        return assets
    
    def _normalize_asset_name(self, entity: str) -> Optional[str]:
        """Normalize asset names to standard symbols"""
        entity_lower = entity.lower()
        
        # Crypto mapping
        crypto_mapping = {
            'bitcoin': 'BTC', 'btc': 'BTC',
            'ethereum': 'ETH', 'eth': 'ETH',
            'cardano': 'ADA', 'ada': 'ADA',
            'solana': 'SOL', 'sol': 'SOL',
            'polygon': 'MATIC', 'matic': 'MATIC',
            'dogecoin': 'DOGE', 'doge': 'DOGE',
            'ripple': 'XRP', 'xrp': 'XRP'
        }
        
        if entity_lower in crypto_mapping:
            return crypto_mapping[entity_lower]
        
        # Stock symbols (uppercase)
        if entity.upper() in ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META']:
            return entity.upper()
        
        return None
    
    def _calculate_volume_proxy(self, data: ProcessedData) -> float:
        """Calculate a volume proxy based on social engagement"""
        volume = 1.0  # Base volume
        
        metadata = data.raw_data.metadata
        if 'likes' in metadata:
            volume += metadata['likes'] * 0.01
        if 'retweets' in metadata:
            volume += metadata['retweets'] * 0.05
        if 'comments' in metadata:
            volume += metadata['comments'] * 0.02
        
        return volume * data.relevance_score
    
    def get_aggregated_sentiment(self, asset: str, window_size: int) -> Optional[AggregatedSentiment]:
        """Get aggregated sentiment for an asset and time window"""
        if asset not in self.sentiment_data:
            return None
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=window_size)
        
        # Filter data within time window
        recent_data = [
            item for item in self.sentiment_data[asset]
            if item['timestamp'] >= cutoff_time
        ]
        
        if not recent_data:
            return None
        
        # Calculate aggregated metrics
        sentiment_scores = [item['sentiment_score'] for item in recent_data]
        confidences = [item['confidence'] for item in recent_data]
        volumes = [item['volume_proxy'] for item in recent_data]
        
        # Weighted averages
        total_volume = sum(volumes)
        if total_volume > 0:
            volume_weighted_score = sum(
                score * volume for score, volume in zip(sentiment_scores, volumes)
            ) / total_volume
        else:
            volume_weighted_score = np.mean(sentiment_scores)
        
        # Calculate momentum (recent vs older sentiment)
        mid_point = len(recent_data) // 2
        if mid_point > 0:
            recent_half = sentiment_scores[mid_point:]
            older_half = sentiment_scores[:mid_point]
            momentum = np.mean(recent_half) - np.mean(older_half)
        else:
            momentum = 0.0
        
        # Source breakdown
        sources_breakdown = defaultdict(lambda: {'count': 0, 'avg_sentiment': 0.0})
        for item in recent_data:
            source = item['source']
            sources_breakdown[source]['count'] += 1
            sources_breakdown[source]['avg_sentiment'] += item['sentiment_score']
        
        for source_data in sources_breakdown.values():
            if source_data['count'] > 0:
                source_data['avg_sentiment'] /= source_data['count']
        
        return AggregatedSentiment(
            asset=asset,
            timestamp=now,
            window_size=window_size,
            total_mentions=len(recent_data),
            sentiment_score=np.mean(sentiment_scores),
            confidence=np.mean(confidences),
            volume_weighted_score=volume_weighted_score,
            momentum=momentum,
            sources_breakdown=dict(sources_breakdown)
        )

class FearGreedCalculator:
    """Calculate Fear & Greed Index"""
    
    def __init__(self):
        self.market_data = deque(maxlen=100)
        self.sentiment_history = deque(maxlen=100)
    
    def add_market_data(self, data: MarketData):
        """Add market data for correlation"""
        self.market_data.append(data)
    
    def calculate_fear_greed_index(self, aggregated_sentiments: Dict[str, AggregatedSentiment]) -> FearGreedIndex:
        """Calculate the Fear & Greed Index"""
        now = datetime.now()
        
        # Component 1: Sentiment (40% weight)
        sentiment_component = self._calculate_sentiment_component(aggregated_sentiments)
        
        # Component 2: Momentum (25% weight)
        momentum_component = self._calculate_momentum_component(aggregated_sentiments)
        
        # Component 3: Volume (20% weight)
        volume_component = self._calculate_volume_component(aggregated_sentiments)
        
        # Component 4: Correlation (15% weight)
        correlation_component = self._calculate_correlation_component()
        
        # Weighted average
        overall_score = (
            sentiment_component * 0.4 +
            momentum_component * 0.25 +
            volume_component * 0.2 +
            correlation_component * 0.15
        )
        
        # Normalize to 0-100 scale
        overall_score = (overall_score + 1) * 50  # Convert from [-1,1] to [0,100]
        overall_score = max(0, min(100, overall_score))
        
        # Classify
        classification = self._classify_fear_greed(overall_score)
        
        return FearGreedIndex(
            timestamp=now,
            overall_score=overall_score,
            sentiment_component=sentiment_component,
            momentum_component=momentum_component,
            volume_component=volume_component,
            correlation_component=correlation_component,
            classification=classification
        )
    
    def _calculate_sentiment_component(self, sentiments: Dict[str, AggregatedSentiment]) -> float:
        """Calculate sentiment component of Fear & Greed Index"""
        if not sentiments:
            return 0.0
        
        weighted_sentiment = 0.0
        total_weight = 0.0
        
        for sentiment in sentiments.values():
            weight = sentiment.total_mentions * sentiment.confidence
            weighted_sentiment += sentiment.volume_weighted_score * weight
            total_weight += weight
        
        return weighted_sentiment / total_weight if total_weight > 0 else 0.0
    
    def _calculate_momentum_component(self, sentiments: Dict[str, AggregatedSentiment]) -> float:
        """Calculate momentum component"""
        if not sentiments:
            return 0.0
        
        momentums = [s.momentum for s in sentiments.values()]
        return np.mean(momentums)
    
    def _calculate_volume_component(self, sentiments: Dict[str, AggregatedSentiment]) -> float:
        """Calculate volume component"""
        if not sentiments:
            return 0.0
        
        # Higher mention volume during positive sentiment = greed
        # Higher mention volume during negative sentiment = fear
        volume_sentiment_product = []
        for sentiment in sentiments.values():
            product = sentiment.total_mentions * sentiment.sentiment_score
            volume_sentiment_product.append(product)
        
        # Normalize
        max_product = max(abs(p) for p in volume_sentiment_product) if volume_sentiment_product else 1
        return np.mean(volume_sentiment_product) / max_product if max_product > 0 else 0.0
    
    def _calculate_correlation_component(self) -> float:
        """Calculate correlation component (simplified)"""
        # This would analyze correlation between sentiment and price movements
        # For now, return a neutral value
        return 0.0
    
    def _classify_fear_greed(self, score: float) -> str:
        """Classify Fear & Greed score"""
        if score <= trading_config.EXTREME_FEAR_THRESHOLD:
            return "Extreme Fear"
        elif score <= trading_config.FEAR_THRESHOLD:
            return "Fear"
        elif score <= trading_config.NEUTRAL_THRESHOLD:
            return "Neutral"
        elif score <= trading_config.GREED_THRESHOLD:
            return "Greed"
        else:
            return "Extreme Greed"

class SignalGenerator:
    """Generate trading signals based on sentiment analysis"""
    
    def __init__(self):
        self.aggregator = SentimentAggregator()
        self.fear_greed_calculator = FearGreedCalculator()
        self.signal_history = deque(maxlen=1000)
        self.last_signals = {}
    
    async def add_processed_data(self, data: ProcessedData):
        """Add processed data for signal generation"""
        self.aggregator.add_sentiment_data(data)
    
    async def add_market_data(self, data: MarketData):
        """Add market data for correlation analysis"""
        self.fear_greed_calculator.add_market_data(data)
    
    async def generate_signals(self) -> List[TradingSignal]:
        """Generate trading signals based on current sentiment"""
        signals = []
        
        # Get aggregated sentiment for different assets and timeframes
        timeframes = [
            processing_config.SHORT_TERM_WINDOW,
            processing_config.MEDIUM_TERM_WINDOW,
            processing_config.LONG_TERM_WINDOW
        ]
        
        for asset in self._get_tracked_assets():
            signal = await self._generate_asset_signal(asset, timeframes)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _get_tracked_assets(self) -> List[str]:
        """Get list of assets to track"""
        # Get assets from aggregator data
        tracked = list(self.aggregator.sentiment_data.keys())
        if not tracked:
            # Default to major assets
            tracked = ['BTC', 'ETH', 'AAPL', 'TSLA', 'MARKET']
        return tracked
    
    async def _generate_asset_signal(self, asset: str, timeframes: List[int]) -> Optional[TradingSignal]:
        """Generate signal for a specific asset"""
        # Get sentiment aggregations for different timeframes
        sentiments = {}
        for timeframe in timeframes:
            sentiment = self.aggregator.get_aggregated_sentiment(asset, timeframe)
            if sentiment:
                sentiments[timeframe] = sentiment
        
        if not sentiments:
            return None
        
        # Calculate Fear & Greed Index
        fear_greed = self.fear_greed_calculator.calculate_fear_greed_index(
            {asset: sentiments[timeframes[0]]} if timeframes[0] in sentiments else {}
        )
        
        # Generate signal based on multi-timeframe analysis
        signal_type, confidence, strength = self._analyze_signal_conditions(
            sentiments, fear_greed
        )
        
        if confidence < trading_config.MIN_SIGNAL_CONFIDENCE:
            return None
        
        # Calculate position size and risk parameters
        position_size = self._calculate_position_size(confidence, strength)
        target_price, stop_loss, take_profit = self._calculate_price_targets(
            asset, signal_type, strength
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(sentiments, fear_greed, signal_type)
        
        signal = TradingSignal(
            asset=asset,
            timestamp=datetime.now(),
            signal_type=signal_type,
            confidence=confidence,
            strength=strength,
            target_price=target_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=self._calculate_risk_reward(stop_loss, take_profit, target_price),
            position_size=position_size,
            reasoning=reasoning,
            supporting_data={
                'fear_greed_score': fear_greed.overall_score,
                'fear_greed_classification': fear_greed.classification,
                'sentiment_scores': {tf: s.sentiment_score for tf, s in sentiments.items()},
                'momentum': {tf: s.momentum for tf, s in sentiments.items()}
            }
        )
        
        # Store signal
        self.signal_history.append(signal)
        self.last_signals[asset] = signal
        
        return signal
    
    def _analyze_signal_conditions(
        self, 
        sentiments: Dict[int, AggregatedSentiment], 
        fear_greed: FearGreedIndex
    ) -> Tuple[SignalType, float, float]:
        """Analyze conditions to determine signal type, confidence, and strength"""
        
        # Get short and medium term sentiment
        short_term = sentiments.get(processing_config.SHORT_TERM_WINDOW)
        medium_term = sentiments.get(processing_config.MEDIUM_TERM_WINDOW)
        
        if not short_term:
            return SignalType.HOLD, 0.0, 0.0
        
        # Base signal on sentiment score and momentum
        sentiment_score = short_term.volume_weighted_score
        momentum = short_term.momentum
        
        # Fear & Greed influence
        fg_influence = self._calculate_fear_greed_influence(fear_greed.overall_score)
        
        # Multi-timeframe confirmation
        confirmation = 1.0
        if medium_term:
            # Check if short and medium term agree
            if (sentiment_score > 0) == (medium_term.sentiment_score > 0):
                confirmation = 1.2
            else:
                confirmation = 0.8
        
        # Signal strength calculation
        strength = abs(sentiment_score) * confirmation * fg_influence
        strength = min(1.0, strength)
        
        # Signal type determination
        combined_score = sentiment_score + momentum * 0.5
        if combined_score > 0.3:
            signal_type = SignalType.BUY
        elif combined_score < -0.3:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        # Confidence calculation
        confidence = min(
            short_term.confidence * confirmation * strength,
            1.0
        )
        
        return signal_type, confidence, strength
    
    def _calculate_fear_greed_influence(self, fg_score: float) -> float:
        """Calculate Fear & Greed influence on signal strength"""
        if fg_score <= trading_config.EXTREME_FEAR_THRESHOLD:
            return 1.3  # Extreme fear = contrarian buy opportunity
        elif fg_score <= trading_config.FEAR_THRESHOLD:
            return 1.1  # Fear = slight buy bias
        elif fg_score >= trading_config.EXTREME_GREED_THRESHOLD:
            return 0.7  # Extreme greed = caution
        elif fg_score >= trading_config.GREED_THRESHOLD:
            return 0.9  # Greed = slight caution
        else:
            return 1.0  # Neutral
    
    def _calculate_position_size(self, confidence: float, strength: float) -> float:
        """Calculate position size based on confidence and strength"""
        base_size = trading_config.MAX_POSITION_SIZE
        size_multiplier = confidence * strength
        return base_size * size_multiplier
    
    def _calculate_price_targets(
        self, asset: str, signal_type: SignalType, strength: float
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate price targets (simplified - would use real market data)"""
        # This is a placeholder - in production would use real price data
        current_price = 50000.0  # Mock current price
        
        if signal_type == SignalType.HOLD:
            return None, None, None
        
        volatility_adjustment = strength * 0.1
        
        if signal_type == SignalType.BUY:
            target_price = current_price * (1 + trading_config.TAKE_PROFIT_PERCENTAGE * volatility_adjustment)
            stop_loss = current_price * (1 - trading_config.STOP_LOSS_PERCENTAGE)
            take_profit = target_price
        else:  # SELL
            target_price = current_price * (1 - trading_config.TAKE_PROFIT_PERCENTAGE * volatility_adjustment)
            stop_loss = current_price * (1 + trading_config.STOP_LOSS_PERCENTAGE)
            take_profit = target_price
        
        return target_price, stop_loss, take_profit
    
    def _calculate_risk_reward(
        self, stop_loss: Optional[float], take_profit: Optional[float], entry_price: Optional[float]
    ) -> Optional[float]:
        """Calculate risk-reward ratio"""
        if not all([stop_loss, take_profit, entry_price]):
            return None
        
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        return reward / risk if risk > 0 else None
    
    def _generate_reasoning(
        self, 
        sentiments: Dict[int, AggregatedSentiment], 
        fear_greed: FearGreedIndex, 
        signal_type: SignalType
    ) -> str:
        """Generate human-readable reasoning for the signal"""
        short_term = sentiments.get(processing_config.SHORT_TERM_WINDOW)
        
        if not short_term:
            return "Insufficient data for signal generation"
        
        reasoning_parts = []
        
        # Sentiment analysis
        sentiment_desc = "positive" if short_term.sentiment_score > 0 else "negative"
        reasoning_parts.append(
            f"Short-term sentiment is {sentiment_desc} ({short_term.sentiment_score:.2f}) "
            f"with {short_term.total_mentions} mentions"
        )
        
        # Momentum
        if abs(short_term.momentum) > 0.1:
            momentum_desc = "increasing" if short_term.momentum > 0 else "decreasing"
            reasoning_parts.append(f"Sentiment momentum is {momentum_desc}")
        
        # Fear & Greed
        reasoning_parts.append(
            f"Fear & Greed Index: {fear_greed.overall_score:.1f} ({fear_greed.classification})"
        )
        
        # Signal rationale
        if signal_type == SignalType.BUY:
            reasoning_parts.append("Bullish sentiment conditions suggest buying opportunity")
        elif signal_type == SignalType.SELL:
            reasoning_parts.append("Bearish sentiment conditions suggest selling opportunity")
        else:
            reasoning_parts.append("Mixed sentiment suggests holding current position")
        
        return ". ".join(reasoning_parts) + "."