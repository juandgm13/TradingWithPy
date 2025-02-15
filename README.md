# TradingWithPy
A desktop-based trading dashboard built with PyQt5 that integrates charting, trading pair information, and customizable UI features like dark mode and interval selection. The dashboard updates trading data in real-time using an API (Binance or Alpaca).

## Features
- 📈 **Real-time Market Data:** Candlestick, volume, depth, RSI, ...
- 🔄 **Multi-Exchange Support:**
  - **Binance**: Fetch market data, manage orders, and track balances.
  - **Alpaca**: Support for both **stocks** and **crypto** trading.
- 🔧 **Extensible Design:** Built with modular components to easily integrate additional exchanges.
- 🖥️ **Windows Native UI:** Desktop-friendly interface with buttons, controls, and charts (Dark mode).
- 📊 **Technical Indicators:** SMA, EMA, and Bollinger Bands with configuration support via JSON.
- 🛒 **Orders Tab:**
  - View real-time **Order Book** for selected trading pairs. [Only with Binace]
  - Place **Buy/Sell** orders with price and quantity inputs. [Currently disabled]
  - Monitor **Open Orders.**
- 🧫 **Testnet Mode:**
  - Enable Binance testnet trading for safe order creation and management.
  - Toggle testnet mode via the `enable_test_trading` parameter in the JSON configuration file.

## Planned Features
- 🔄 **Additional Exchange Integrations.**
- 📊 **Strategy Backtesting & Automated Trading.**
- 🔔 **Notification System:** Alerts for significant price changes.

## Trading Dashboard Overview
![image](https://github.com/user-attachments/assets/36949205-3aa0-4135-a495-7ab9062536b1)

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
1. Create an `.env` file in the root directory and add your API keys:  
```plaintext
# Binance API Keys  
BINANCE_API_KEY=your_api_key  
BINANCE_API_SECRET=your_api_secret  
BINANCE_API_KEY_TEST=your_api_key (for TEST)  
BINANCE_API_SECRET_TEST=your_api_secret (for TEST)  

# Alpaca API Keys  
ALPACA_API_KEY=your_api_key  
ALPACA_API_SECRET=your_api_secret
ALPACA_API_KEY_TEST=your_api_key (for TEST)
ALPACA_API_SECRET_TEST=your_api_secret (for TEST)
```

## Usage

### Run the Application
```bash
python app/main.py  
```

### Basic Functionality
1. Launch the UI.  
2. Select an **exchange** (Binance or Alpaca).  
3. Fetch **real-time market data.**  
4. Enable/disable indicators (**SMA, EMA, Bollinger Bands**) via UI checkboxes.  
5. Customize indicator settings and enable test mode using the `config.json` file.  

## File Structure
```plaintext
trading-dashboard/  
├── app/  
│   ├── api/  
│   │   ├── api_manager.py       # API manager handling Binance & Alpaca  
│   │   ├── binance_api.py       # Binance API implementation  
│   │   └── alpaca_api.py        # Alpaca API implementation (stocks & crypto)  
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
This project is licensed under the **MIT License.**

## Acknowledgments
- **Binance API**: Official Python SDK for Binance.  
- **Alpaca API**: For stocks & crypto trading.  
- **PyQt**: Used for building the desktop UI.  
- **PyQtGraph**: For interactive trading charts.  

