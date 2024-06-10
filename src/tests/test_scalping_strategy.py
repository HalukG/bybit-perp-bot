import unittest
from unittest.mock import MagicMock
from strategies.scalping_strategy import ScalpingStrategy
from utils.bybit_client import BybitClient
import pandas as pd

class TestScalpingStrategy(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=BybitClient)
        self.strategy = ScalpingStrategy(self.mock_client)
        self.mock_client.LinearPositions.Linear_positions_saveLeverage.return_value = {'ret_code': 0}
        self.mock_client.LinearOrder.LinearOrder_new.return_value = {'ret_code': 0}

    def test_apply_strategy(self):
        # Mock the data from Bybit API
        self.mock_client.LinearKline.LinearKline_get.return_value = (
            {'ret_code': 0, 'result': [
                {'open_time': 1625097600000, 'open': 2000.0, 'high': 2005.0, 'low': 1995.0, 'close': 2003.0, 'volume': 100.0}
            ] * 100}, None
        )

        self.strategy.apply_strategy()
        self.mock_client.LinearKline.LinearKline_get.assert_called_once_with(symbol='ETHUSDT', interval='1', limit=100)

        # Simulate conditions for a bullish entry
        self.mock_client.LinearKline.LinearKline_get.return_value[0]['result'][-1]['close'] = 2002.0
        self.strategy.position = None
        self.strategy.apply_strategy()
        self.assertEqual(self.strategy.position, 'long')

        # Simulate conditions for a bullish exit
        self.mock_client.LinearKline.LinearKline_get.return_value[0]['result'][-1]['close'] = 1990.0
        self.strategy.position = 'long'
        self.strategy.apply_strategy()
        self.assertEqual(self.strategy.position, None)

        # Simulate conditions for a bearish entry
        self.mock_client.LinearKline.LinearKline_get.return_value[0]['result'][-1]['close'] = 1990.0
        self.strategy.position = None
        self.strategy.apply_strategy()
        self.assertEqual(self.strategy.position, 'short')

        # Simulate conditions for a bearish exit
        self.mock_client.LinearKline.LinearKline_get.return_value[0]['result'][-1]['close'] = 2000.0
        self.strategy.position = 'short'
        self.strategy.apply_strategy()
        self.assertEqual(self.strategy.position, None)

if __name__ == '__main__':
    unittest.main()
