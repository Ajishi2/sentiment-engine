"""
Demo script to showcase the Fear & Greed Sentiment Engine
"""
import asyncio
import logging
from datetime import datetime
import sys

from main import demo_mode

if __name__ == "__main__":
    print("=" * 80)
    print("FEAR & GREED SENTIMENT ENGINE - DEMONSTRATION")
    print("=" * 80)
    print()
    print("This demo will showcase the sentiment analysis engine with:")
    print("• Real-time data ingestion from multiple sources")
    print("• Advanced NLP sentiment analysis with financial context")
    print("• Fear & Greed Index calculation")
    print("• Trading signal generation")
    print("• Backtesting and performance evaluation")
    print()
    print("The demo will run for 5 minutes using mock data...")
    print("Press Ctrl+C at any time to stop.")
    print("=" * 80)
    print()
    
    try:
        asyncio.run(demo_mode())
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")
    except Exception as e:
        logging.error(f"Demo error: {e}")
        sys.exit(1)