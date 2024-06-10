import importlib
import os
import sys
import asyncio

# Adjust the system path to include the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.bybit_client import BybitClient

class TradingBot:
    def __init__(self):
        self.client = BybitClient().get_client()
        strategy_module = importlib.import_module(f"strategies.scalping_strategy")
        self.strategy = strategy_module.ScalpingStrategy(self.client)

    async def start(self):
        self.strategy.run()

if __name__ == "__main__":
    bot = TradingBot()
    bot.start()
