# Fear & Greed Sentiment Engine

A high-performance sentiment analysis and trade signal generation system that aggregates real-time data from social media, news feeds, and financial sources to generate actionable trading signals based on market psychology.

## 🚀 Features

### Core Capabilities
- **Multi-Source Data Ingestion**: Real-time processing from Twitter, Reddit, news feeds, and financial data
- **Advanced NLP Analysis**: Financial sentiment analysis using transformer models (FinBERT) with entity recognition
- **Fear & Greed Index**: Proprietary calculation based on sentiment, momentum, volume, and correlation analysis
- **Signal Generation**: AI-powered trading signals with confidence scoring and risk management
- **Real-Time Processing**: High-throughput pipeline capable of processing 10,000+ posts per minute
- **Backtesting Framework**: Comprehensive strategy evaluation with performance metrics

### Technical Architecture
- **Asynchronous Processing**: Multi-threaded pipeline for optimal performance
- **Modular Design**: Clean separation of concerns for maintainability
- **Error Handling**: Robust connection management and graceful degradation
- **Monitoring**: Real-time dashboard with performance metrics

## 📊 Dashboard

The system includes a comprehensive real-time dashboard featuring:
- Fear & Greed Index gauge
- Live sentiment analysis charts
- Trading signal generation
- Performance metrics and backtesting results
- Asset-specific sentiment breakdown

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd sentiment-engine
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download NLTK data**
```python
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
```

4. **Configure API keys** (optional for demo)
Create a `.env` file with your API keys:
```
TWITTER_BEARER_TOKEN=your_twitter_token
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
NEWS_API_KEY=your_news_api_key
```

## 🎯 Quick Start

### Demo Mode
Run the engine in demonstration mode with mock data:
```bash
python run_demo.py
```

### Dashboard Mode
Launch the real-time dashboard:
```bash
python dashboard/app.py
```
Then open http://localhost:8050 in your browser.

### Production Mode
Start the full engine:
```bash
python main.py
```

## 📈 System Architecture

### Data Pipeline
1. **Ingestion Layer**: Multi-source data collection (Twitter, Reddit, News, Financial)
2. **Processing Layer**: NLP sentiment analysis with financial context
3. **Analysis Layer**: Aggregation, correlation, and signal generation
4. **Output Layer**: Trading signals, backtesting, and visualization

### Core Components

#### Data Ingestion (`core/data_ingestion.py`)
- `TwitterIngestion`: Real-time Twitter stream processing
- `RedditIngestion`: Reddit post and comment analysis
- `NewsIngestion`: Financial news aggregation
- `FinancialDataIngestion`: Market data correlation

#### Sentiment Analysis (`core/sentiment_analyzer.py`)
- `AdvancedSentimentAnalyzer`: Multi-model sentiment analysis
- `FinancialEntityExtractor`: Asset and financial term recognition
- `SentimentProcessor`: Real-time processing pipeline

#### Signal Generation (`core/signal_generator.py`)
- `SentimentAggregator`: Multi-timeframe sentiment aggregation
- `FearGreedCalculator`: Proprietary fear & greed index
- `SignalGenerator`: AI-powered trading signal generation

#### Backtesting (`core/backtesting.py`)
- `BacktestEngine`: Strategy performance evaluation
- `Portfolio`: Position management and risk control
- `PerformanceMetrics`: Comprehensive analysis framework

## 🎛️ Configuration

The system is highly configurable through `config.py`:

### Processing Configuration
- Sentiment models and thresholds
- Time windows and batch sizes
- Text processing parameters

### Trading Configuration
- Fear & Greed Index thresholds
- Signal confidence requirements
- Risk management parameters

### Data Configuration
- Supported assets and keywords
- Social media sources
- News feed configurations

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Sentiment Accuracy**: Model confidence and validation scores
- **Signal Performance**: Win rate, profit factor, Sharpe ratio
- **System Performance**: Processing speed, latency, throughput
- **Risk Metrics**: Maximum drawdown, correlation exposure

## 🔬 Advanced Features

### Machine Learning
- Pre-trained financial language models (FinBERT)
- Custom sentiment classification for financial contexts
- Multi-language support and sarcasm detection
- Real-time model inference optimization

### Risk Management
- Position sizing based on signal confidence
- Correlation-based exposure limits
- Dynamic stop-loss and take-profit levels
- Portfolio-level risk monitoring

### Analytics
- Cross-asset sentiment contagion analysis
- Market regime classification
- Behavioral bias detection
- Sentiment-price correlation studies

## 🧪 Backtesting

The framework includes comprehensive backtesting capabilities:

```python
from core.backtesting import run_strategy_backtest

# Run backtest with generated signals
result = await run_strategy_backtest(signals)
print(f"Total Return: {result.total_return:.2%}")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Max Drawdown: {result.max_drawdown:.2%}")
```

## 📚 API Reference

### Core Classes

#### `SentimentEngine`
Main engine orchestrating all components.

#### `SentimentScore`
Sentiment analysis result with polarity, confidence, and emotions.

#### `TradingSignal`
Trading recommendation with confidence, risk metrics, and reasoning.

#### `FearGreedIndex`
Comprehensive market psychology indicator.

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
flake8 core/
black core/
```

### Logging
The system provides comprehensive logging:
- File logging: `sentiment_engine.log`
- Console output with configurable levels
- Performance and error tracking

## 🚀 Production Deployment

### Performance Optimization
- Memory pools for text processing
- SIMD instructions for numerical computations
- Lock-free data structures for high-frequency updates
- GPU acceleration for ML inference

### Scaling Considerations
- Horizontal scaling with message queues
- Database optimization for historical data
- Caching strategies for frequently accessed data
- Load balancing for multiple data sources

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 🆘 Support

For questions and support:
- Check the documentation
- Review the configuration options
- Examine the logs for debugging
- Open an issue for bugs or feature requests

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core sentiment analysis engine
- ✅ Multi-source data ingestion
- ✅ Basic signal generation
- ✅ Backtesting framework

### Phase 2 (Upcoming)
- 🔄 Advanced ML models integration
- 🔄 Real-time dashboard enhancements
- 🔄 Database persistence layer
- 🔄 API endpoints for external integration

### Phase 3 (Future)
- 📋 Alternative data sources integration
- 📋 Advanced risk management features
- 📋 Cloud deployment optimization
- 📋 Mobile application support

---

**Built with Python 3.9+, featuring async/await patterns, modern NLP models, and production-ready architecture.**