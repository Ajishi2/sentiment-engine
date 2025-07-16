import React from 'react';
import { motion } from 'framer-motion';

interface FearGreedGaugeProps {
  score: number;
  size?: number;
  showDetails?: boolean;
}

const FearGreedGauge: React.FC<FearGreedGaugeProps> = ({ 
  score, 
  size = 200, 
  showDetails = true 
}) => {
  const getFearGreedColor = (score: number) => {
    if (score <= 25) return '#DC2626'; // Extreme Fear
    if (score <= 45) return '#EA580C'; // Fear
    if (score <= 55) return '#D97706'; // Neutral
    if (score <= 75) return '#059669'; // Greed
    return '#16A34A'; // Extreme Greed
  };

  const getFearGreedLabel = (score: number) => {
    if (score <= 25) return 'Extreme Fear';
    if (score <= 45) return 'Fear';
    if (score <= 55) return 'Neutral';
    if (score <= 75) return 'Greed';
    return 'Extreme Greed';
  };

  const radius = size / 2 - 20;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
        viewBox={`0 0 ${size} ${size}`}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth="12"
          fill="none"
          className="text-slate-600"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={getFearGreedColor(score)}
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
        
        {/* Gradient definitions */}
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#DC2626" />
            <stop offset="25%" stopColor="#EA580C" />
            <stop offset="50%" stopColor="#D97706" />
            <stop offset="75%" stopColor="#059669" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* Center content */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            className="text-4xl font-bold mb-1"
            style={{ color: getFearGreedColor(score) }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
          >
            {Math.round(score)}
          </motion.div>
          {showDetails && (
            <motion.div
              className="text-sm text-slate-400 font-medium"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              {getFearGreedLabel(score)}
            </motion.div>
          )}
        </div>
      </div>
      
      {/* Score markers */}
      {showDetails && (
        <div className="absolute inset-0">
          {[0, 25, 50, 75, 100].map((value, index) => {
            const angle = (value / 100) * 360 - 90;
            const x = size / 2 + (radius + 15) * Math.cos((angle * Math.PI) / 180);
            const y = size / 2 + (radius + 15) * Math.sin((angle * Math.PI) / 180);
            
            return (
              <div
                key={value}
                className="absolute text-xs text-slate-500 font-medium"
                style={{
                  left: x - 8,
                  top: y - 8,
                  transform: 'translate(-50%, -50%)'
                }}
              >
                {value}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default FearGreedGauge;