# TradingWithPy
A desktop-based trading dashboard built with PyQt5 that integrates charting, trading pair information, and customizable UI features like dark mode and interval selection. The dashboard updates trading data in real time using an API (e.g., Binance).

## Features
- 📈 Real-time candlestick, volume, and depth charts.
- 🔄 Binance Integration: Fetch market data, manage orders, and track balances via Binance API.
- 🔧 Extensible Design: Built with modular components to easily add support for other exchanges.
- 🖥️ Windows Native UI: Desktop-friendly interface with buttons, controls, and charts. (Dark mode)

## Planned Features
- Support for additional exchanges (via modular API integration).
- Built-in technical analysis tools (e.g., Moving Averages, RSI).
- Strategy backtesting and automated trading.
- Notification System: Push alerts for significant price changes.
- Trading Actions: Allow placing market/limit orders directly from the dashboard.

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
```

## Usage
### Run the Application
```bash
python app/main.py
```
### Basic Functionality
1. Launch the UI.
2. Fetch real-time market data.

## File Structure
```plantext
trading-dashboard/
├── app/
│   ├── api/
│   │   ├── api_wrapper.py       # API interactions (e.g., Binance API)
│   │   └── binance_api.py       # Binance Api implementation
│   ├── ui/
│   │   ├── charts.py            # Chart widget implementations
│   │   └── main_window.py       # Main PyQt5 GUI layout and logic
│   └── utils/
│       └── logger.py            # Custom logger setup
├── main.py                      # Main entry point of the application
└── README.md                    # Project documentation
```

## License
This project is licensed under the MIT License.

## Acknowledgments
- Binance API: Official Python SDK for Binance.
- PyQt: For building the desktop UI.
- PyQtGraph: For interactive trading charts.