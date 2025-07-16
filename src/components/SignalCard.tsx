import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Target, Shield, Clock } from 'lucide-react';

interface SignalCardProps {
  signal: {
    asset: string;
    signal: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    strength: number;
    reasoning: string;
    timestamp: string;
    targetPrice?: number;
    stopLoss?: number;
    riskReward?: number;
  };
  index: number;
}

const SignalCard: React.FC<SignalCardProps> = ({ signal, index }) => {
  const getSignalIcon = (signalType: string) => {
    switch (signalType) {
      case 'BUY': return <TrendingUp className="w-5 h-5" />;
      case 'SELL': return <TrendingDown className="w-5 h-5" />;
      default: return <Minus className="w-5 h-5" />;
    }
  };

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'BUY': return {
        bg: 'from-green-500/20 to-green-600/10',
        border: 'border-green-500/30',
        text: 'text-green-400',
        badge: 'bg-green-500/20 text-green-400'
      };
      case 'SELL': return {
        bg: 'from-red-500/20 to-red-600/10',
        border: 'border-red-500/30',
        text: 'text-red-400',
        badge: 'bg-red-500/20 text-red-400'
      };
      default: return {
        bg: 'from-gray-500/20 to-gray-600/10',
        border: 'border-gray-500/30',
        text: 'text-gray-400',
        badge: 'bg-gray-500/20 text-gray-400'
      };
    }
  };

  const colors = getSignalColor(signal.signal);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.1, type: "spring", stiffness: 100 }}
      className={`bg-gradient-to-br ${colors.bg} rounded-xl p-6 border ${colors.border} backdrop-blur-sm`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${colors.badge}`}>
            {getSignalIcon(signal.signal)}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">{signal.asset}</h3>
            <span className={`text-sm font-medium ${colors.text}`}>
              {signal.signal} Signal
            </span>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-2xl font-bold text-white">
            {Math.round(signal.confidence * 100)}%
          </div>
          <div className="text-xs text-slate-400">Confidence</div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-semibold text-white">
            {Math.round(signal.strength * 100)}%
          </div>
          <div className="text-xs text-slate-400 flex items-center justify-center">
            <Target className="w-3 h-3 mr-1" />
            Strength
          </div>
        </div>
        
        {signal.riskReward && (
          <div className="text-center">
            <div className="text-lg font-semibold text-white">
              {signal.riskReward.toFixed(1)}:1
            </div>
            <div className="text-xs text-slate-400 flex items-center justify-center">
              <Shield className="w-3 h-3 mr-1" />
              Risk/Reward
            </div>
          </div>
        )}
        
        <div className="text-center">
          <div className="text-lg font-semibold text-white">
            {new Date(signal.timestamp).toLocaleTimeString()}
          </div>
          <div className="text-xs text-slate-400 flex items-center justify-center">
            <Clock className="w-3 h-3 mr-1" />
            Generated
          </div>
        </div>
      </div>

      {/* Price Targets */}
      {(signal.targetPrice || signal.stopLoss) && (
        <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-slate-800/50 rounded-lg">
          {signal.targetPrice && (
            <div>
              <div className="text-xs text-slate-400 mb-1">Target Price</div>
              <div className="text-sm font-semibold text-green-400">
                ${signal.targetPrice.toLocaleString()}
              </div>
            </div>
          )}
          {signal.stopLoss && (
            <div>
              <div className="text-xs text-slate-400 mb-1">Stop Loss</div>
              <div className="text-sm font-semibold text-red-400">
                ${signal.stopLoss.toLocaleString()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reasoning */}
      <div className="bg-slate-800/30 rounded-lg p-3">
        <div className="text-xs text-slate-400 mb-1">Analysis</div>
        <p className="text-sm text-slate-300 leading-relaxed">
          {signal.reasoning}
        </p>
      </div>

      {/* Confidence Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Signal Confidence</span>
          <span>{Math.round(signal.confidence * 100)}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <motion.div
            className={`h-2 rounded-full ${colors.text.replace('text-', 'bg-')}`}
            initial={{ width: 0 }}
            animate={{ width: `${signal.confidence * 100}%` }}
            transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default SignalCard;