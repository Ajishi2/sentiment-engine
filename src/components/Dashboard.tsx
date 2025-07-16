import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
   TrendingDown, Activity, Database, Globe, 
  BarChart3, PieChart, Zap, AlertTriangle, 
  DollarSign, Target,  Users, Brain
} from 'lucide-react';
import { AreaChart, Area, PieChart as RechartsPieChart, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Pie, Line } from 'recharts';

interface SentimentData {
  id: string;
  source: string;
  content: string;
  sentiment: number;
  confidence: number;
  entity: string;
  timestamp: string;
  author: string;
}

interface TradingSignal {
  asset: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  strength: number;
  reasoning: string;
  timestamp: string;
  targetPrice?: number;
  stopLoss?: number;
  riskReward?: number;
}

interface FearGreedData {
  score: number;
  classification: string;
  components: {
    sentiment: number;
    momentum: number;
    volume: number;
    correlation: number;
  };
}

const Dashboard: React.FC = () => {
  const [sentimentData, setSentimentData] = useState<SentimentData[]>([]);
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [fearGreedIndex, setFearGreedIndex] = useState<FearGreedData>({
    score: 73,
    classification: 'Greed',
    components: { sentiment: 0.68, momentum: 0.45, volume: 0.82, correlation: 0.34 }
  });
  const [systemStats, setSystemStats] = useState({
    dataSources: 4,
    processingRate: 8200,
    winRate: 68.4,
    sharpeRatio: 1.82,
    maxDrawdown: -12.3,
    alphaGeneration: 15.7
  });

  const [isLoading, setIsLoading] = useState(true);

  // Mock real-time data updates
  useEffect(() => {
    // Initialize with some data
    const initialData: SentimentData[] = [
      {
        id: 'initial_1',
        source: 'Twitter',
        content: 'Bitcoin breaking through resistance! 🚀 This bull run is just getting started #BTC',
        sentiment: 0.85,
        confidence: 0.92,
        entity: 'BTC',
        timestamp: new Date().toISOString(),
        author: 'crypto_trader_pro'
      },
      {
        id: 'initial_2',
        source: 'Reddit',
        content: 'Market looking bearish. Fed policy uncertainty causing selloff',
        sentiment: -0.72,
        confidence: 0.88,
        entity: 'MARKET',
        timestamp: new Date().toISOString(),
        author: 'market_analyst'
      }
    ];

    const initialSignals: TradingSignal[] = [
      {
        asset: 'BTC',
        signal: 'BUY',
        confidence: 0.89,
        strength: 0.92,
        reasoning: 'Strong bullish sentiment with institutional backing. Fear & Greed Index showing greed territory',
        timestamp: new Date().toISOString(),
        targetPrice: 52000,
        stopLoss: 48000,
        riskReward: 2.1
      }
    ];

    setSentimentData(initialData);
    setSignals(initialSignals);
    setIsLoading(false);

    const interval = setInterval(() => {
      // Update sentiment data
      const newSentiment: SentimentData = {
        id: `sentiment_${Date.now()}`,
        source: ['Twitter', 'Reddit', 'News', 'Financial'][Math.floor(Math.random() * 4)],
        content: generateMockContent(),
        sentiment: (Math.random() - 0.5) * 2,
        confidence: 0.7 + Math.random() * 0.3,
        entity: ['BTC', 'ETH', 'TSLA', 'AAPL', 'MARKET'][Math.floor(Math.random() * 5)],
        timestamp: new Date().toISOString(),
        author: `user_${Math.floor(Math.random() * 9999)}`
      };

      setSentimentData(prev => [newSentiment, ...prev.slice(0, 49)]);

      // Occasionally generate new signals
      if (Math.random() < 0.1) {
        const newSignal: TradingSignal = {
          asset: ['BTC', 'ETH', 'TSLA', 'AAPL'][Math.floor(Math.random() * 4)],
          signal: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)] as 'BUY' | 'SELL' | 'HOLD',
          confidence: 0.6 + Math.random() * 0.4,
          strength: 0.4 + Math.random() * 0.6,
          reasoning: generateSignalReasoning(),
          timestamp: new Date().toISOString(),
          targetPrice: 45000 + Math.random() * 10000,
          stopLoss: 42000 + Math.random() * 3000,
          riskReward: 1.5 + Math.random() * 2
        };

        setSignals(prev => [newSignal, ...prev.slice(0, 9)]);
        
        // Show toast notification for new signals
        if (newSignal.signal !== 'HOLD') {
          console.log(`New ${newSignal.signal} signal for ${newSignal.asset}`);
        }
      }

      // Update Fear & Greed Index
      setFearGreedIndex(prev => ({
        ...prev,
        score: Math.max(0, Math.min(100, prev.score + (Math.random() - 0.5) * 5)),
        components: {
          sentiment: Math.max(0, Math.min(1, prev.components.sentiment + (Math.random() - 0.5) * 0.1)),
          momentum: Math.max(0, Math.min(1, prev.components.momentum + (Math.random() - 0.5) * 0.1)),
          volume: Math.max(0, Math.min(1, prev.components.volume + (Math.random() - 0.5) * 0.1)),
          correlation: Math.max(0, Math.min(1, prev.components.correlation + (Math.random() - 0.5) * 0.1))
        }
      }));

    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const generateMockContent = () => {
    const contents = [
      "Bitcoin breaking through resistance! 🚀 This bull run is just getting started. Target $60K by end of month #BTC #crypto",
      "Market looking very bearish right now. Fed policy uncertainty causing major selloff. Time to be cautious with positions 📉",
      "Major investment bank announces comprehensive cryptocurrency trading services, signaling growing institutional adoption",
      "Ethereum network upgrade showing promising performance improvements. DeFi ecosystem expanding rapidly",
      "Technical analysis suggests potential breakout above key resistance levels. Volume confirming bullish momentum",
      "Fear and uncertainty dominating market sentiment. Contrarian indicators suggesting potential reversal opportunity",
      "Institutional flows showing increased allocation to digital assets. Long-term outlook remains positive",
      "Market volatility creating opportunities for skilled traders. Risk management crucial in current environment"
    ];
    return contents[Math.floor(Math.random() * contents.length)];
  };

  const generateSignalReasoning = () => {
    const reasons = [
      "Strong bullish sentiment with institutional backing. Fear & Greed Index showing greed territory",
      "Negative sentiment momentum with high volatility concerns. Risk-adjusted signal strength",
      "Mixed sentiment signals. Waiting for clearer directional bias. DeFi developments positive",
      "Correlation analysis indicates potential breakout. Volume patterns supporting bullish thesis",
      "Contrarian signal based on extreme fear readings. Historical patterns suggest reversal",
      "Technical indicators aligning with sentiment analysis. Multi-timeframe confirmation"
    ];
    return reasons[Math.floor(Math.random() * reasons.length)];
  };

  const getFearGreedColor = (score: number) => {
    if (score <= 25) return '#DC2626'; // Extreme Fear - Red
    if (score <= 45) return '#EA580C'; // Fear - Orange
    if (score <= 55) return '#D97706'; // Neutral - Amber
    if (score <= 75) return '#059669'; // Greed - Green
    return '#16A34A'; // Extreme Greed - Dark Green
  };

  const getFearGreedLabel = (score: number) => {
    if (score <= 25) return 'Extreme Fear';
    if (score <= 45) return 'Fear';
    if (score <= 55) return 'Neutral';
    if (score <= 75) return 'Greed';
    return 'Extreme Greed';
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return '#059669';
    if (sentiment < -0.3) return '#DC2626';
    return '#6B7280';
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY': return '#059669';
      case 'SELL': return '#DC2626';
      default: return '#6B7280';
    }
  };

  // Generate chart data
  const sentimentChartData = sentimentData.slice(0, 20).reverse().map((item, index) => ({
    time: new Date(item.timestamp).toLocaleTimeString(),
    sentiment: item.sentiment,
    confidence: item.confidence
  }));

  const assetBreakdown = sentimentData.reduce((acc, item) => {
    acc[item.entity] = (acc[item.entity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const pieData = Object.entries(assetBreakdown).map(([name, value]) => ({ name, value }));
  const COLORS = ['#2563EB', '#059669', '#DC2626', '#D97706', '#7C3AED'];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold mb-2">Initializing Sentiment Engine</h2>
          <p className="text-slate-400">Loading real-time data streams...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="w-8 h-8 text-blue-400" />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  Fear & Greed Sentiment Engine
                </h1>
              </div>
              <div className="flex items-center space-x-2 text-sm text-green-400">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Live Processing</span>
              </div>
            </div>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-blue-400" />
                <span>Supabase Connected</span>
              </div>
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-green-400" />
                <span>{systemStats.dataSources} Data Sources</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-purple-400" />
                <span>{systemStats.processingRate.toLocaleString()} posts/min</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Top Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Win Rate</p>
                <p className="text-2xl font-bold text-green-400">{systemStats.winRate}%</p>
              </div>
              <Target className="w-8 h-8 text-green-400" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Sharpe Ratio</p>
                <p className="text-2xl font-bold text-blue-400">{systemStats.sharpeRatio}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-400" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Max Drawdown</p>
                <p className="text-2xl font-bold text-red-400">{systemStats.maxDrawdown}%</p>
              </div>
              <TrendingDown className="w-8 h-8 text-red-400" />
            </div>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Alpha Generation</p>
                <p className="text-2xl font-bold text-purple-400">+{systemStats.alphaGeneration}%</p>
              </div>
              <Zap className="w-8 h-8 text-purple-400" />
            </div>
          </motion.div>
        </div>

        {/* Main Dashboard Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Fear & Greed Index */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <PieChart className="w-5 h-5 mr-2 text-blue-400" />
              Fear & Greed Index
            </h3>
            
            <div className="relative w-48 h-48 mx-auto mb-4">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className="text-slate-600"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke={getFearGreedColor(fearGreedIndex.score)}
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 40}`}
                  strokeDashoffset={`${2 * Math.PI * 40 * (1 - fearGreedIndex.score / 100)}`}
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-3xl font-bold" style={{ color: getFearGreedColor(fearGreedIndex.score) }}>
                    {Math.round(fearGreedIndex.score)}
                  </div>
                  <div className="text-sm text-slate-400">
                    {getFearGreedLabel(fearGreedIndex.score)}
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Sentiment</span>
                <span className="text-sm font-medium">{Math.round(fearGreedIndex.components.sentiment * 100)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Momentum</span>
                <span className="text-sm font-medium">{Math.round(fearGreedIndex.components.momentum * 100)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Volume</span>
                <span className="text-sm font-medium">{Math.round(fearGreedIndex.components.volume * 100)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Correlation</span>
                <span className="text-sm font-medium">{Math.round(fearGreedIndex.components.correlation * 100)}%</span>
              </div>
            </div>
          </motion.div>

          {/* Active Signals */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-yellow-400" />
              Active Signals
            </h3>
            
            <div className="space-y-4 max-h-80 overflow-y-auto">
                {signals.map((signal, index) => (
                  <motion.div
                    key={`${signal.asset}-${signal.timestamp}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold">{signal.asset}</span>
                        <span 
                          className="px-2 py-1 rounded text-xs font-medium"
                          style={{ 
                            backgroundColor: `${getSignalColor(signal.signal)}20`,
                            color: getSignalColor(signal.signal)
                          }}
                        >
                          {signal.signal}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{Math.round(signal.confidence * 100)}%</div>
                        <div className="text-xs text-slate-400">confidence</div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-slate-300 mb-2">{signal.reasoning}</p>
                    
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Strength: {Math.round(signal.strength * 100)}%</span>
                      <span>{new Date(signal.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </motion.div>
                ))}
            </div>
          </motion.div>

          {/* Asset Breakdown */}
          <motion.div 
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
          >
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2 text-green-400" />
              Asset Sentiment
            </h3>
            
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      border: '1px solid #475569',
                      borderRadius: '8px'
                    }}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-2 mt-4">
              {pieData.slice(0, 5).map((item, index) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: COLORS[index % COLORS.length] }}
                    ></div>
                    <span className="text-sm">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium">{item.value}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Sentiment Timeline */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 border border-slate-600"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-purple-400" />
            Real-time Sentiment Analysis
          </h3>
          
          <div className="h-64 mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sentimentChartData}>
                <defs>
                  <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="time" 
                  stroke="#9CA3AF"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  fontSize={12}
                  domain={[-1, 1]}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #475569',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="sentiment"
                  stroke="#3B82F6"
                  fillOpacity={1}
                  fill="url(#sentimentGradient)"
                />
                <Line
                  type="monotone"
                  dataKey="confidence"
                  stroke="#10B981"
                  strokeWidth={2}
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Live Feed */}
          <div className="space-y-3 max-h-64 overflow-y-auto">
            <h4 className="text-sm font-semibold text-slate-400 flex items-center">
              <Users className="w-4 h-4 mr-2" />
              Live Sentiment Feed
            </h4>
              {sentimentData.slice(0, 5).map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-slate-700/30 rounded-lg p-3 border border-slate-600/50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">
                        {item.source}
                      </span>
                      <span className="text-xs text-slate-400">
                        @{item.author} • {new Date(item.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span 
                        className="text-sm font-bold"
                        style={{ color: getSentimentColor(item.sentiment) }}
                      >
                        {item.sentiment > 0 ? '+' : ''}{item.sentiment.toFixed(2)}
                      </span>
                      <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-400 rounded">
                        {item.entity}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm text-slate-300 mb-2">{item.content}</p>
                  
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span>
                      Sentiment: {item.sentiment > 0.3 ? 'Bullish' : item.sentiment < -0.3 ? 'Bearish' : 'Neutral'}
                    </span>
                    <span>Confidence: {Math.round(item.confidence * 100)}%</span>
                  </div>
                </motion.div>
              ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;