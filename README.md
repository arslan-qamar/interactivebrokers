# IBKR TWS Data Stream with MACD Crossover Strategy

## Overview
This project is a quick Proof of Concept (PoC) demonstrating how to connect to the Interactive Brokers Trader Workstation (IBKR TWS) using Python. It streams real-time market data for a specified stock symbol and runs a simple Moving Average Convergence Divergence (MACD) Crossover Strategy.

**⚠ Disclaimer:** This project is for educational proof of concept and testing purposes only. It is NOT intended for production use or real trading. Use at your own RISK !!

## Features
- Connects to IBKR TWS via the `ibapi` library
- Streams real-time market data for a specified stock symbol
- Implements a basic MACD Crossover Strategy
- Prints price and size updates to the console

## Requirements
Ensure you have the following installed before running the script:

- Python 3.7+
- Interactive Brokers TWS or IB Gateway (running and connected)
- Required Python packages (see `requirements.txt`)

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Usage
1. **Start IBKR TWS or IB Gateway**
   - Ensure API access is enabled in TWS under **Edit > Global Configuration > API > Settings**.
   - Set **Socket Port** to `7497` (for paper trading) or `7496` (for live trading).
   - Enable **Read-Only API** or uncheck it for write access.

2. **Run the Script**
   ```sh
   python main.py
   ```
   The script connects to IBKR TWS and begins streaming market data for the specified stock symbol.

## Configuration
Modify the contract details in `main.py` to specify the stock symbol, exchange, and security type:
```python
contract.symbol = "AAPL"  # Change this to the desired stock symbol
contract.secType = "STK"   # Security type (e.g., 'STK' for stocks, 'CASH' for forex)
contract.currency = "USD"
contract.exchange = "SMART"  # Use appropriate exchange
```

## MACD Crossover Strategy (Planned Feature)
A simple MACD crossover strategy will be implemented:
- Calculates MACD line and signal line
- Identifies buy/sell signals based on crossovers
- Prints trade signals to the console

## Known Issues
- Requires an active IBKR TWS session
- Only streams price and size updates, does not support order execution
- Limited error handling

## Future Improvements
- Implement order execution for backtesting
- Add logging and better error handling
- Improve strategy and performance optimizations

## License
This project is open-source and available under the MIT License.

## Contact
For any questions or improvements, feel free to contribute or raise an issue.

