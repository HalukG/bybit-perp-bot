# Bybit Perpetual Futures Trading Bot

This high-performance trading bot is designed to trade ETH perpetual futures on Bybit using a scalping strategy on low timeframes. It can run locally or on the cloud and includes unit tests for the strategy.

## Features

- Trades ETH with 20x leverage on low timeframes
- Implements a scalping strategy with dynamic profit-taking targets based on market conditions
- Asynchronous operations for improved performance
- Detailed logging for order placements, cancellations, and closures
- Configurable via environment variables

## Requirements

- Docker and Docker Compose installed
- Bybit API key and secret

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/bybit-perp-bot.git
cd bybit-perp-bot
```

### 2. Environment Variables
Create a .env file in the root directory with your Bybit API credentials:
```
BYBIT_API_KEY=your_api_key
BYBIT_API_SECRET=your_api_secret
```

### 3. Build and Run with Docker
```bash
docker-compose build
docker-compose up
```

## Bot configuration

`bybit_client.py`
Handles communication with the Bybit API, including placing, canceling, and modifying orders asynchronously.

`scalping_strategy.py`
Implements the scalping strategy with dynamic take-profit and stop-loss logic based on market conditions.

`bot.py`
Initializes and runs the trading bot.

## TODO
- [ ] Add more advanced trading strategies
- [ ] Improve error handling and retry logic
- [ ] Implement additional unit tests
- [ ] Add support for multiple trading pairs
- [ ] Enhance configuration options via environment variables

## License 
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer
Trading cryptocurrencies involves significant risk and can result in the loss of your invested capital. Use this bot at your own risk.