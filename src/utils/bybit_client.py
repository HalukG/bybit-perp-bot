from pybit.unified_trading import HTTP
import os
import aiohttp
import asyncio

class BybitClient:
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.client = HTTP(
            testnet=False,
            api_key=self.api_key,
            api_secret=self.api_secret
        )

    async def get_kline(self, category, symbol, interval, limit):
        async with aiohttp.ClientSession() as session:
            return await self.client.get_kline(
                category=category,
                symbol=symbol,
                interval=interval,
                limit=limit
            )

    async def place_order(self, category, symbol, side, order_type, qty, time_in_force, takeProfit=None, stopLoss=None, tpOrderType='Market', slOrderType='Market', reduceOnly=False):
        async with aiohttp.ClientSession() as session:
            return await self.client.place_active_order(
                category=category,
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=qty,
                timeInForce=time_in_force,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpOrderType=tpOrderType,
                slOrderType=slOrderType,
                reduceOnly=reduceOnly
            )

    async def cancel_order(self, category, symbol, order_id):
        async with aiohttp.ClientSession() as session:
            return await self.client.cancel_order(
                category=category,
                symbol=symbol,
                orderId=order_id
            )
