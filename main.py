"""
Main application entry point for the Fear & Greed Sentiment Engine
"""
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import List

from config import api_config, processing_config, trading_config
from core.data_ingestion import DataIngestionManager
from core.sentiment_analyzer import SentimentProcessor
from core.signal_generator import SignalGenerator
from core.backtesting import run_strategy_backtest
from core.data_models import ProcessedData, TradingSignal
from database.supabase_client import db_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sentiment_engine.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SentimentEngine:
    """Main Fear & Greed Sentiment Engine"""
    
    def __init__(self):
        self.data_manager = DataIngestionManager()
        self.sentiment_processor = SentimentProcessor()
        self.signal_generator = SignalGenerator()
        self.is_running = False
        self.processed_data_queue = asyncio.Queue()
        self.signals_queue = asyncio.Queue()
        self.generated_signals = []
    
    async def start(self):
        """Start the sentiment engine"""
        logger.info("Starting Fear & Greed Sentiment Engine...")
        
        self.is_running = True
        
        # Start all components
        tasks = [
            asyncio.create_task(self.data_manager.start_all()),
            asyncio.create_task(self.sentiment_processor.start_processing()),
            asyncio.create_task(self._process_data_pipeline()),
            asyncio.create_task(self._generate_signals_pipeline()),
            asyncio.create_task(self._monitor_performance())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
            await self.stop()
    
    async def stop(self):
        """Stop the sentiment engine"""
        logger.info("Stopping Fear & Greed Sentiment Engine...")
        
        self.is_running = False
        
        # Stop all components
        await self.data_manager.stop_all()
        await self.sentiment_processor.stop_processing()
        
        logger.info("Sentiment engine stopped")
    
    async def _process_data_pipeline(self):
        """Main data processing pipeline"""
        while self.is_running:
            try:
                # This would be connected to the data ingestion manager
                # For now, we'll simulate the processing
                await asyncio.sleep(1)
                
                # In production, this would receive processed data from sentiment analyzer
                # and forward it to signal generator
                
            except Exception as e:
                logger.error(f"Error in data processing pipeline: {e}")
                await asyncio.sleep(5)
    
    async def _generate_signals_pipeline(self):
        """Signal generation pipeline"""
        while self.is_running:
            try:
                # Generate signals every 60 seconds
                signals = await self.signal_generator.generate_signals()
                
                for signal in signals:
                    await self.signals_queue.put(signal)
                    self.generated_signals.append(signal)
                    logger.info(f"Generated {signal.signal_type.value} signal for {signal.asset} "
                              f"(confidence: {signal.confidence:.2f})")
                
                await asyncio.sleep(60)  # Generate signals every minute
                
            except Exception as e:
                logger.error(f"Error in signal generation pipeline: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_performance(self):
        """Monitor system performance and run periodic backtests"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                if len(self.generated_signals) >= 10:  # Need minimum signals for backtest
                    logger.info("Running performance backtest...")
                    
                    # Get recent signals for backtesting
                    recent_signals = self.generated_signals[-50:]  # Last 50 signals
                    
                    # Run backtest
                    backtest_result = await run_strategy_backtest(recent_signals)
                    
                    logger.info(f"Backtest Results:")
                    logger.info(f"  Total Return: {backtest_result.total_return:.2%}")
                    logger.info(f"  Sharpe Ratio: {backtest_result.sharpe_ratio:.2f}")
                    logger.info(f"  Max Drawdown: {backtest_result.max_drawdown:.2%}")
                    logger.info(f"  Win Rate: {backtest_result.win_rate:.2%}")
                    logger.info(f"  Total Trades: {backtest_result.total_trades}")
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
    
    async def get_latest_signals(self, count: int = 10) -> List[TradingSignal]:
        """Get the latest generated signals"""
        return self.generated_signals[-count:] if self.generated_signals else []
    
    async def get_system_status(self) -> dict:
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'total_signals_generated': len(self.generated_signals),
            'data_sources_active': len(self.data_manager.sources),
            'last_signal_time': self.generated_signals[-1].timestamp if self.generated_signals else None,
            'queue_sizes': {
                'processed_data': self.processed_data_queue.qsize(),
                'signals': self.signals_queue.qsize()
            }
        }

async def demo_mode():
    """Run the engine in demonstration mode"""
    logger.info("Starting Fear & Greed Sentiment Engine in Demo Mode")
    logger.info("=" * 60)
    
    engine = SentimentEngine()
    
    # Run for a limited time in demo mode
    try:
        # Start the engine
        start_task = asyncio.create_task(engine.start())
        
        # Run for 5 minutes in demo mode
        await asyncio.sleep(300)
        
        # Get final status and results
        status = await engine.get_system_status()
        latest_signals = await engine.get_latest_signals(5)
        
        logger.info("=" * 60)
        logger.info("DEMO RESULTS:")
        logger.info(f"System Status: {status}")
        logger.info(f"Latest Signals Generated: {len(latest_signals)}")
        
        for i, signal in enumerate(latest_signals, 1):
            logger.info(f"  Signal {i}: {signal.signal_type.value} {signal.asset} "
                       f"(confidence: {signal.confidence:.2f}, strength: {signal.strength:.2f})")
            logger.info(f"    Reasoning: {signal.reasoning}")
        
        # Run a final backtest if we have signals
        if latest_signals:
            logger.info("\nRunning final backtest...")
            backtest_result = await run_strategy_backtest(latest_signals)
            
            logger.info("BACKTEST RESULTS:")
            logger.info(f"  Strategy: {backtest_result.strategy_name}")
            logger.info(f"  Period: {backtest_result.start_date} to {backtest_result.end_date}")
            logger.info(f"  Total Return: {backtest_result.total_return:.2%}")
            logger.info(f"  Sharpe Ratio: {backtest_result.sharpe_ratio:.2f}")
            logger.info(f"  Max Drawdown: {backtest_result.max_drawdown:.2%}")
            logger.info(f"  Win Rate: {backtest_result.win_rate:.2%}")
            logger.info(f"  Profit Factor: {backtest_result.profit_factor:.2f}")
            logger.info(f"  Total Trades: {backtest_result.total_trades}")
            logger.info(f"  Avg Trade Duration: {backtest_result.avg_trade_duration:.1f} hours")
        
        # Stop the engine
        await engine.stop()
        
    except Exception as e:
        logger.error(f"Error in demo mode: {e}")
        await engine.stop()

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        await demo_mode()
    else:
        # Production mode
        engine = SentimentEngine()
        try:
            await engine.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await engine.stop()

if __name__ == "__main__":
    asyncio.run(main())