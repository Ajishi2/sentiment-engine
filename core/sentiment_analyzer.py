"""
Advanced sentiment analysis engine with financial context
"""
import asyncio
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np

# NLP libraries
import nltk
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

from config import processing_config
from core.data_models import RawData, ProcessedData, SentimentScore, SentimentPolarity

logger = logging.getLogger(__name__)

class FinancialEntityExtractor:
    """Extract financial entities from text"""
    
    def __init__(self):
        # Financial keywords and patterns
        self.crypto_patterns = [
            r'\b(bitcoin|btc|ethereum|eth|cardano|ada|solana|sol|polygon|matic|dogecoin|doge|ripple|xrp)\b',
            r'\$[A-Z]{2,5}\b',  # Ticker symbols
            r'\b[A-Z]{2,5}/USD\b'  # Trading pairs
        ]
        
        self.stock_patterns = [
            r'\b(AAPL|GOOGL|MSFT|TSLA|AMZN|NVDA|META|NFLX|BABA|CRM)\b',
            r'\$[A-Z]{1,5}\b'  # Stock tickers
        ]
        
        self.financial_terms = [
            'bull market', 'bear market', 'bullish', 'bearish', 'pump', 'dump',
            'hodl', 'fomo', 'fud', 'diamond hands', 'paper hands', 'moon', 'dip',
            'support', 'resistance', 'breakout', 'breakdown', 'volume', 'market cap'
        ]
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract financial entities from text"""
        entities = []
        text_lower = text.lower()
        
        # Extract crypto entities
        for pattern in self.crypto_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            entities.extend(matches)
        
        # Extract stock entities
        for pattern in self.stock_patterns:
            matches = re.findall(pattern, text.upper())
            entities.extend(matches)
        
        # Extract financial terms
        for term in self.financial_terms:
            if term in text_lower:
                entities.append(term)
        
        return list(set(entities))  # Remove duplicates

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analysis with financial context"""
    
    def __init__(self):
        self.entity_extractor = FinancialEntityExtractor()
        self.models_initialized = False
        self.financial_model = None
        self.general_model = None
        self.tokenizer = None
        
        # Initialize models asynchronously
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """Initialize ML models"""
        try:
            logger.info("Initializing sentiment analysis models...")
            
            # Initialize financial sentiment model (FinBERT)
            try:
                self.financial_model = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                logger.info("FinBERT model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load FinBERT model: {e}")
                # Fallback to general model
                self.financial_model = None
            
            # Initialize general sentiment model
            self.general_model = pipeline("sentiment-analysis")
            
            self.models_initialized = True
            logger.info("Sentiment analysis models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Fallback to TextBlob only
            self.models_initialized = False
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags for cleaner analysis (but keep the content)
        text = re.sub(r'@\w+|#', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit length
        if len(text) > processing_config.MAX_TEXT_LENGTH:
            text = text[:processing_config.MAX_TEXT_LENGTH]
        
        return text
    
    def _textblob_sentiment(self, text: str) -> Tuple[float, float]:
        """Get sentiment using TextBlob as fallback"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        confidence = abs(polarity) * (1 - subjectivity)  # More objective = more confident
        return polarity, min(confidence, 1.0)
    
    def _transformer_sentiment(self, text: str, model) -> Tuple[float, float]:
        """Get sentiment using transformer model"""
        if not model:
            return self._textblob_sentiment(text)
        
        try:
            result = model(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            # Convert to polarity scale (-1 to 1)
            if 'positive' in label or 'bullish' in label:
                polarity = score
            elif 'negative' in label or 'bearish' in label:
                polarity = -score
            else:  # neutral
                polarity = 0
            
            confidence = score
            return polarity, confidence
            
        except Exception as e:
            logger.warning(f"Transformer model error: {e}, falling back to TextBlob")
            return self._textblob_sentiment(text)
    
    def _calculate_financial_boost(self, text: str, entities: List[str]) -> float:
        """Calculate sentiment boost based on financial context"""
        boost = 1.0
        text_lower = text.lower()
        
        # Positive financial indicators
        positive_indicators = ['moon', 'bullish', 'pump', 'breakout', 'rally', 'surge', 'bull run']
        negative_indicators = ['dump', 'bearish', 'crash', 'selloff', 'bear market', 'fud']
        
        for indicator in positive_indicators:
            if indicator in text_lower:
                boost += 0.1
        
        for indicator in negative_indicators:
            if indicator in text_lower:
                boost -= 0.1
        
        # Entity relevance boost
        if entities:
            boost += len(entities) * 0.05
        
        return max(0.1, min(2.0, boost))  # Clamp between 0.1 and 2.0
    
    def _classify_polarity(self, score: float) -> SentimentPolarity:
        """Classify sentiment score into polarity enum"""
        if score <= -0.6:
            return SentimentPolarity.VERY_NEGATIVE
        elif score <= -0.2:
            return SentimentPolarity.NEGATIVE
        elif score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentPolarity.POSITIVE
        else:
            return SentimentPolarity.NEUTRAL
    
    async def analyze_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment of text with financial context"""
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Extract financial entities
        entities = self.entity_extractor.extract_entities(processed_text)
        
        # Get sentiment scores
        if self.models_initialized and self.financial_model and entities:
            # Use financial model for finance-related content
            polarity, confidence = self._transformer_sentiment(processed_text, self.financial_model)
        elif self.models_initialized and self.general_model:
            # Use general model
            polarity, confidence = self._transformer_sentiment(processed_text, self.general_model)
        else:
            # Fallback to TextBlob
            polarity, confidence = self._textblob_sentiment(processed_text)
        
        # Apply financial context boost
        financial_boost = self._calculate_financial_boost(processed_text, entities)
        adjusted_polarity = polarity * financial_boost
        adjusted_polarity = max(-1.0, min(1.0, adjusted_polarity))  # Clamp to [-1, 1]
        
        # Calculate emotions (simplified)
        emotions = {
            "fear": max(0, -adjusted_polarity) if adjusted_polarity < 0 else 0,
            "greed": max(0, adjusted_polarity) if adjusted_polarity > 0 else 0,
            "uncertainty": 1 - confidence,
            "confidence": confidence
        }
        
        return SentimentScore(
            polarity=self._classify_polarity(adjusted_polarity),
            confidence=confidence,
            score=adjusted_polarity,
            emotions=emotions,
            entities=entities
        )

class SentimentProcessor:
    """Process raw data through sentiment analysis pipeline"""
    
    def __init__(self):
        self.analyzer = AdvancedSentimentAnalyzer()
        self.processing_queue = asyncio.Queue()
        self.results_queue = asyncio.Queue()
        self.is_processing = False
    
    async def start_processing(self):
        """Start the sentiment processing pipeline"""
        self.is_processing = True
        # Start processing tasks
        tasks = [
            asyncio.create_task(self._process_data()),
            asyncio.create_task(self._batch_process())
        ]
        await asyncio.gather(*tasks)
    
    async def stop_processing(self):
        """Stop the sentiment processing pipeline"""
        self.is_processing = False
    
    async def add_data(self, raw_data: RawData):
        """Add raw data to processing queue"""
        await self.processing_queue.put(raw_data)
    
    async def get_processed_data(self) -> ProcessedData:
        """Get processed data with sentiment analysis"""
        return await self.results_queue.get()
    
    async def _process_data(self):
        """Main data processing loop"""
        while self.is_processing:
            try:
                # Get data from queue with timeout
                raw_data = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=1.0
                )
                
                # Analyze sentiment
                sentiment = await self.analyzer.analyze_sentiment(raw_data.content)
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(raw_data, sentiment)
                
                # Create processed data
                processed_data = ProcessedData(
                    raw_data=raw_data,
                    sentiment=sentiment,
                    financial_entities=sentiment.entities,
                    relevance_score=relevance_score,
                    language="en"  # Simplified - could add language detection
                )
                
                # Add to results queue
                await self.results_queue.put(processed_data)
                
            except asyncio.TimeoutError:
                # No data in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing sentiment data: {e}")
    
    async def _batch_process(self):
        """Batch processing for efficiency"""
        batch = []
        while self.is_processing:
            try:
                # Collect batch
                while len(batch) < processing_config.BATCH_SIZE:
                    try:
                        data = await asyncio.wait_for(
                            self.processing_queue.get(), 
                            timeout=0.1
                        )
                        batch.append(data)
                    except asyncio.TimeoutError:
                        if batch:  # Process partial batch
                            break
                        else:
                            await asyncio.sleep(0.1)
                            continue
                
                if batch:
                    # Process batch (could be optimized for transformer models)
                    tasks = [self._process_single_item(item) for item in batch]
                    await asyncio.gather(*tasks)
                    batch.clear()
                
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
    
    async def _process_single_item(self, raw_data: RawData):
        """Process a single item (used in batch processing)"""
        # This would be optimized for batch processing in production
        await self.add_data(raw_data)
    
    def _calculate_relevance(self, raw_data: RawData, sentiment: SentimentScore) -> float:
        """Calculate relevance score for the data"""
        relevance = 0.5  # Base relevance
        
        # Boost relevance based on financial entities
        if sentiment.entities:
            relevance += len(sentiment.entities) * 0.1
        
        # Boost based on source metadata (likes, retweets, etc.)
        if raw_data.metadata:
            if 'likes' in raw_data.metadata:
                relevance += min(raw_data.metadata['likes'] / 1000, 0.3)
            if 'retweets' in raw_data.metadata:
                relevance += min(raw_data.metadata['retweets'] / 100, 0.2)
        
        # Boost based on sentiment confidence
        relevance += sentiment.confidence * 0.2
        
        return min(1.0, relevance)  # Cap at 1.0