import pandas as pd
import ta
import asyncio
import logging
from strategies.strategy_template import StrategyTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScalpingStrategy(StrategyTemplate):
    def __init__(self, client):
        super().__init__(client)
        self.symbol = 'ETHUSDT'
        self.leverage = 20
        logging.info("Initializing ScalpingStrategy")
        self.position = None  # None, 'long', 'short'
        self.open_orders = []

    async def fetch_data(self):
        logging.info("Fetching market data")
        response = await self.client.get_kline(category='linear', symbol=self.symbol, interval='1m', limit=100)
        if 'retCode' in response and response['retCode'] == 0:
            candles = response['result']['list']
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
            df['close'] = df['close'].astype(float)
            return df
        else:
            logging.error(f"Failed to fetch market data: {response}")
            return None

    def calculate_indicators(self, df):
        df['SMA_5'] = ta.trend.sma_indicator(df['close'], window=5)
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['RSI_14'] = ta.momentum.rsi(df['close'], window=14)
        bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['BB_upper'] = bollinger.bollinger_hband()
        df['BB_lower'] = bollinger.bollinger_lband()
        df['BB_middle'] = bollinger.bollinger_mavg()
        return df

    def get_last_indicators(self, df):
        last_close = df['close'].iloc[-1]
        last_sma_5 = df['SMA_5'].iloc[-1]
        last_ema_20 = df['EMA_20'].iloc[-1]
        last_rsi_14 = df['RSI_14'].iloc[-1]
        last_bb_upper = df['BB_upper'].iloc[-1]
        last_bb_lower = df['BB_lower'].iloc[-1]
        last_bb_middle = df['BB_middle'].iloc[-1]
        return last_close, last_sma_5, last_ema_20, last_rsi_14, last_bb_upper, last_bb_lower, last_bb_middle

    async def cancel_open_orders(self):
        for order_id in self.open_orders:
            await self.client.cancel_order(
                category='linear',
                symbol=self.symbol,
                order_id=order_id
            )
            logging.info(f"Canceled order {order_id}")
        self.open_orders = []

    async def enter_long_position(self):
        stop_loss = self.calculate_stop_loss('long')
        order = await self.client.place_order(
            category='linear',
            symbol=self.symbol,
            side='Buy',
            order_type='Market',
            qty='0.1',  # Define quantity based on your risk management
            time_in_force='GTC',
            stopLoss=stop_loss,    
            slOrderType='Limit'
        )
        if 'result' in order:
            self.position = 'long'
            self.open_orders.append(order['result']['orderId'])
            logging.info(f"Placed long order {order['result']['orderId']}")
        else:
            logging.error(f"Failed to enter long position: {order}")

    async def enter_short_position(self):
        stop_loss = self.calculate_stop_loss('short')
        order = await self.client.place_order(
            category='linear',
            symbol=self.symbol,
            side='Sell',
            order_type='Market',
            qty='0.1',  # Define quantity based on your risk management
            time_in_force='GTC',
            stopLoss=stop_loss,    
            slOrderType='Limit'
        )
        if 'result' in order:
            self.position = 'short'
            self.open_orders.append(order['result']['orderId'])
            logging.info(f"Placed short order {order['result']['orderId']}")
        else:
            logging.error(f"Failed to enter short position: {order}")

    async def exit_long_position(self):
        await self.cancel_open_orders()
        order = await self.client.place_order(
            category='linear',
            symbol=self.symbol,
            side='Sell',
            order_type='Market',
            qty='0.1',  # Define quantity based on your risk management
            time_in_force='GTC',
            reduceOnly=True
        )
        if 'result' in order:
            self.position = None
            self.open_orders.append(order['result']['orderId'])
            logging.info(f"Exited long position with order {order['result']['orderId']}")
        else:
            logging.error(f"Failed to exit long position: {order}")

    async def exit_short_position(self):
        await self.cancel_open_orders()
        order = await self.client.place_order(
            category='linear',
            symbol=self.symbol,
            side='Buy',
            order_type='Market',
            qty='0.1',  # Define quantity based on your risk management
            time_in_force='GTC',
            reduceOnly=True
        )
        if 'result' in order:
            self.position = None
            self.open_orders.append(order['result']['orderId'])
            logging.info(f"Exited short position with order {order['result']['orderId']}")
        else:
            logging.error(f"Failed to exit short position: {order}")

    def calculate_take_profit(self, last_close, position_type):
        # Adjust take-profit based on market conditions
        # Placeholder logic for take-profit calculation
        if position_type == 'long':
            return str(last_close * 1.02)  # Example: 2% above the last close
        else:
            return str(last_close * 0.98)  # Example: 2% below the last close

    def calculate_stop_loss(self, position_type):
        # Stop-loss is always 2% from the entry price
        last_close = self.get_last_indicators(self.fetch_data())[0]
        if position_type == 'long':
            return str(last_close * 0.98)
        else:
            return str(last_close * 1.02)

    async def apply_strategy(self):
        df = await self.fetch_data()
        if df is not None:
            df = self.calculate_indicators(df)
            last_close, last_sma_5, last_ema_20, last_rsi_14, last_bb_upper, last_bb_lower, last_bb_middle = self.get_last_indicators(df)

            # Check for bullish entry
            if last_close > last_sma_5 and last_sma_5 > last_ema_20 and last_rsi_14 > 30 and last_close <= last_bb_lower and self.position is None:
                await self.enter_long_position()

            # Check for bearish entry
            elif last_close < last_sma_5 and last_sma_5 < last_ema_20 and last_rsi_14 < 70 and last_close >= last_bb_upper and self.position is None:
                await self.enter_short_position()

            # Check for bullish exit or take-profit
            if self.position == 'long':
                take_profit = self.calculate_take_profit(last_close, 'long')
                if last_close >= float(take_profit) or last_close < last_sma_5 or last_sma_5 < last_ema_20 or last_rsi_14 < 70:
                    await self.exit_long_position()

            # Check for bearish exit or take-profit
            if self.position == 'short':
                take_profit = self.calculate_take_profit(last_close, 'short')
                if last_close <= float(take_profit) or last_close > last_sma_5 or last_sma_5 > last_ema_20 or last_rsi_14 > 30:
                    await self.exit_short_position()

    async def run(self):
        logging.info("Starting trading bot")
        while True:
            try:
                await self.apply_strategy()
                await asyncio.sleep(60)  # Wait for the next minute candle
            except Exception as e:
                logging.error(f"Error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
