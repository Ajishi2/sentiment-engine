-- Create tables for the Fear & Greed Sentiment Engine

-- Raw data from various sources
CREATE TABLE IF NOT EXISTS raw_data (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    content TEXT NOT NULL,
    author TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Processed sentiment data
CREATE TABLE IF NOT EXISTS processed_data (
    id BIGSERIAL PRIMARY KEY,
    raw_data_id TEXT REFERENCES raw_data(id),
    sentiment_score FLOAT NOT NULL,
    sentiment_polarity INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    emotions JSONB DEFAULT '{}',
    entities JSONB DEFAULT '[]',
    relevance_score FLOAT DEFAULT 0.0,
    language TEXT DEFAULT 'en',
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trading signals generated by the engine
CREATE TABLE IF NOT EXISTS trading_signals (
    id BIGSERIAL PRIMARY KEY,
    asset TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    signal_type TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    strength FLOAT NOT NULL,
    target_price FLOAT,
    stop_loss FLOAT,
    take_profit FLOAT,
    risk_reward_ratio FLOAT,
    position_size FLOAT DEFAULT 0.0,
    reasoning TEXT,
    supporting_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fear & Greed Index calculations
CREATE TABLE IF NOT EXISTS fear_greed_index (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    overall_score FLOAT NOT NULL,
    sentiment_component FLOAT NOT NULL,
    momentum_component FLOAT NOT NULL,
    volume_component FLOAT NOT NULL,
    correlation_component FLOAT NOT NULL,
    classification TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Market data for correlation analysis
CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    symbol TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    price FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    change_24h FLOAT NOT NULL,
    market_cap FLOAT,
    additional_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Backtesting results
CREATE TABLE IF NOT EXISTS backtest_results (
    id BIGSERIAL PRIMARY KEY,
    strategy_name TEXT NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    total_return FLOAT NOT NULL,
    sharpe_ratio FLOAT NOT NULL,
    max_drawdown FLOAT NOT NULL,
    win_rate FLOAT NOT NULL,
    profit_factor FLOAT NOT NULL,
    total_trades INTEGER NOT NULL,
    avg_trade_duration FLOAT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Aggregated sentiment for quick queries
CREATE TABLE IF NOT EXISTS aggregated_sentiment (
    id BIGSERIAL PRIMARY KEY,
    asset TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    window_size INTEGER NOT NULL,
    total_mentions INTEGER NOT NULL,
    sentiment_score FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    volume_weighted_score FLOAT NOT NULL,
    momentum FLOAT NOT NULL,
    sources_breakdown JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_raw_data_timestamp ON raw_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_raw_data_source ON raw_data(source);
CREATE INDEX IF NOT EXISTS idx_processed_data_timestamp ON processed_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_signals_asset ON trading_signals(asset);
CREATE INDEX IF NOT EXISTS idx_trading_signals_timestamp ON trading_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_fear_greed_timestamp ON fear_greed_index(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_aggregated_sentiment_asset ON aggregated_sentiment(asset);
CREATE INDEX IF NOT EXISTS idx_aggregated_sentiment_timestamp ON aggregated_sentiment(timestamp);

-- Enable Row Level Security (RLS)
ALTER TABLE raw_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE processed_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE fear_greed_index ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE aggregated_sentiment ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Allow authenticated users to read all data" ON raw_data
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert raw data" ON raw_data
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read processed data" ON processed_data
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert processed data" ON processed_data
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read trading signals" ON trading_signals
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert trading signals" ON trading_signals
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read fear greed index" ON fear_greed_index
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert fear greed index" ON fear_greed_index
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read market data" ON market_data
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert market data" ON market_data
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read backtest results" ON backtest_results
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert backtest results" ON backtest_results
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated users to read aggregated sentiment" ON aggregated_sentiment
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated users to insert aggregated sentiment" ON aggregated_sentiment
    FOR INSERT TO authenticated WITH CHECK (true);