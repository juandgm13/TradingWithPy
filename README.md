# TradingWithPy
A desktop-based trading dashboard built with PyQt5 that integrates charting, trading pair information, and customizable UI features like dark mode and interval selection. The dashboard updates trading data in real time using an API (e.g., Binance).

## Features
- 📈 Real-time candlestick, volume, and depth charts.
- 🔄 Binance Integration: Fetch market data, manage orders, and track balances via Binance API.
- 🔧 Extensible Design: Built with modular components to easily add support for other exchanges.
- 🖥️ Windows Native UI: Desktop-friendly interface with buttons, controls, and charts. (Dark mode)
- 📊 Technical Indicators: Added support for SMA, EMA, Bollinger Bands with the ability to toggle indicators on/off using checkboxes and load their configurations from a JSON file.
- 🛒 Orders Tab: Manage orders with ease: View real-time Order Book for the selected trading pair. Place Buy or Sell orders with price and quantity inputs and monitor Open Orders.
- 🧪 Testnet Mode: Enable Binance testnet trading for safe order creation and management: Toggle testnet mode with the enable_test_trading parameter in the JSON configuration file.
  
## Planned Features
- Support for additional exchanges (via modular API integration).
- Strategy backtesting and automated trading.
- Notification System: Push alerts for significant price changes.

## Trading Dashboard Overview
![image](https://github.com/user-attachments/assets/1611bdaa-bba7-4097-8da0-60cd3b004e69)

## Installation

### Clone the Repository
```bash
git clone https://github.com/juandgm13/TradingWithPy.git
cd TradingWithPy
```

### Prerequisites
1. Install Python 3.8+.
2. Install required dependencies:
```bash
pip install -r requirements.txt
```
### Set Up API Keys
1. Create an .env file in the root directory:
```plaintext
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_API_KEY_TEST=your_api_key (for testnet)
BINANCE_API_SECRET_TEST=your_api_secret (for testnet)
```

## Usage
### Run the Application
```bash
python app/main.py
```
### Basic Functionality
1. Launch the UI.
2. Fetch real-time market data.
3. Enable/disable indicators (SMA, EMA, Bollinger Bands) using checkboxes in the UI.
4. Customize indicator settings and enable test mode through a config.json file for dynamic configuration.

## File Structure
```plantext
trading-dashboard/
├── app/
│   ├── api/
│   │   ├── api_wrapper.py       # API interactions (e.g., Binance API)
│   │   └── binance_api.py       # Binance Api implementation
│   ├── ui/
│   │   ├── charts.py            # Chart widget implementations
│   │   ├── tabs_definition.py   # Tabs widget implementations
│   │   └── main_window.py       # Main PyQt5 GUI layout and logic
│   └── utils/         
│       ├── logger.py            # Custom logger setup
│       ├── indicators.py        # Indicator calculations (SMA, EMA, Bollinger Bands)  
│       └── config/
│           ├── config_loader.py # Loads configuration from JSON file
│           └── config.json      # Configuration file  
├── main.py                      # Main entry point of the application
└── README.md                    # Project documentation
```

## License
This project is licensed under the MIT License.

## Acknowledgments
- Binance API: Official Python SDK for Binance.
- PyQt: For building the desktop UI.
- PyQtGraph: For interactive trading charts.
