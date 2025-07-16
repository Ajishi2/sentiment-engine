import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types
export interface SentimentData {
  id: string;
  source: string;
  content: string;
  sentiment_score: number;
  confidence: number;
  entities: string[];
  timestamp: string;
  author: string;
  metadata: Record<string, any>;
}

export interface TradingSignal {
  id: number;
  asset: string;
  signal_type: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  strength: number;
  reasoning: string;
  timestamp: string;
  target_price?: number;
  stop_loss?: number;
  take_profit?: number;
  risk_reward_ratio?: number;
}

export interface FearGreedIndex {
  id: number;
  timestamp: string;
  overall_score: number;
  sentiment_component: number;
  momentum_component: number;
  volume_component: number;
  correlation_component: number;
  classification: string;
}

// API functions
export const fetchLatestSentiment = async (limit = 50) => {
  const { data, error } = await supabase
    .from('processed_data')
    .select('*')
    .order('timestamp', { ascending: false })
    .limit(limit);
  
  if (error) throw error;
  return data;
};

export const fetchTradingSignals = async (limit = 10) => {
  const { data, error } = await supabase
    .from('trading_signals')
    .select('*')
    .order('timestamp', { ascending: false })
    .limit(limit);
  
  if (error) throw error;
  return data;
};

export const fetchFearGreedIndex = async () => {
  const { data, error } = await supabase
    .from('fear_greed_index')
    .select('*')
    .order('timestamp', { ascending: false })
    .limit(1)
    .single();
  
  if (error) throw error;
  return data;
};

export const subscribeToSentiment = (callback: (payload: any) => void) => {
  return supabase
    .channel('sentiment_updates')
    .on('postgres_changes', 
      { event: 'INSERT', schema: 'public', table: 'processed_data' },
      callback
    )
    .subscribe();
};

export const subscribeToSignals = (callback: (payload: any) => void) => {
  return supabase
    .channel('signal_updates')
    .on('postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'trading_signals' },
      callback
    )
    .subscribe();
};