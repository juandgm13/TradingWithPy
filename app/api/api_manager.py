import os
from app.utils.logger import setup_logger
from app.api.binance_api import BinanceAPI
from app.api.alpaca_api import AlpacaAPI
from app.utils.config import ConfigLoader

class APIManager:
    def __init__(self, api_name="binance", logger=None):
        """
        Initializes the API Manager with the selected API (Binance, Alpaca Stocks, or Alpaca Crypto).

        :param api_name: The name of the API ("binance", "alpaca-stock", "alpaca-crypto").
        :param logger: Logger instance (optional).
        """
        self.logger = logger if logger else setup_logger()
        self.config = ConfigLoader("app/utils/config/config.json")
        self.enable_test_trading = self.config.get("enable_test_trading", False)
        
        # Initialize APIs
        self.api_clients = {
            "binance": self._init_binance(),
            "alpaca-stock": self._init_alpaca(stock=True),
            "alpaca-crypto": self._init_alpaca(stock=False),
        }

        self.api_name = None
        self.api_client = None
        self.set_api(api_name)

    def _init_binance(self):
        """Initializes the Binance API client."""
        api_key = os.environ.get('BINANCE_API_KEY_TEST' if self.enable_test_trading else 'BINANCE_API_KEY')
        api_secret = os.environ.get('BINANCE_API_SECRET_TEST' if self.enable_test_trading else 'BINANCE_API_SECRET')

        if not api_key or not api_secret:
            self.logger.warning("Connecting to Binance without API Key or Secret.")
            return BinanceAPI(logger=self.logger)

        return BinanceAPI(api_key=api_key, api_secret=api_secret, logger=self.logger, test_enabled=self.enable_test_trading)

    def _init_alpaca(self, stock=True):
        """Initializes the Alpaca API client for stocks or crypto."""
        api_key = os.environ.get('ALPACA_API_KEY_TEST' if self.enable_test_trading else 'ALPACA_API_KEY')
        api_secret = os.environ.get('ALPACA_API_SECRET_TEST' if self.enable_test_trading else 'ALPACA_API_SECRET')

        if not api_key or not api_secret:
            self.logger.error("Alpaca API credentials are missing.")
            return None

        return AlpacaAPI(api_key=api_key, api_secret=api_secret, logger=self.logger, test_enabled=self.enable_test_trading, stock=stock)


    def set_api(self, api_name):
        """
        Switches the active API.

        :param api_name: The new API to use ("binance", "alpaca-stock", "alpaca-crypto").
        """
        if api_name not in self.api_clients:
            raise ValueError(f"Unsupported API: {api_name}")

        self.api_name = api_name
        self.api_client = self.api_clients[api_name]
        self.logger.info(f"APIManager switched to {api_name}.")

    def get_api_clients_list(self):
        """
        Returns a list of available API client names.

        :return: List of API names.
        """
        return list(self.api_clients.keys())

    def get_trading_symbols(self, api_name=None):
        """
        Fetches all available trading pairs (symbols) from the current API.
        :return: List of trading symbols.
        """
        if(api_name):
            if api_name not in self.api_clients:
                raise ValueError(f"Unsupported API: {api_name}")
            else:
                return self.api_clients[api_name].get_trading_symbols()
        else:
            return self.api_client.get_trading_symbols()

    def get_candlestick_data(self, trading_pair, interval='1h', limit=100, api_name=None):
        """
        Fetches candlestick data for a given trading pair.

        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param interval: Candlestick interval (default: '1h').
        :param limit: Number of candlesticks to fetch (default: 100).
        :return: List of candlestick data.
        """
        if(api_name):
            if api_name not in self.api_clients:
                raise ValueError(f"Unsupported API: {api_name}")
            else:
                return self.api_clients[api_name].get_candlestick_data(trading_pair, interval, limit)
        else:
            return self.api_client.get_candlestick_data(trading_pair, interval, limit)

    def get_depth_data(self, trading_pair, limit=100):
        """
        Fetches depth data for a given trading pair.

        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param limit: Number of levels to fetch (default: 100).
        :return: Depth data (bids and asks).
        """
        return self.api_client.get_depth_data(trading_pair, limit)

    def get_ticker_info(self, trading_pair, api_name=None):
        """
        Fetches ticker information for the given trading pair.

        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :return: A dictionary containing price, change, high, low, and volume.
        """
        if(api_name):
            if api_name not in self.api_clients:
                raise ValueError(f"Unsupported API: {api_name}")
            else:
                return self.api_clients[api_name].get_ticker_info(trading_pair)
        else:
            return self.api_client.get_ticker_info(trading_pair)

    def get_open_orders(self, pair):
        """
        Fetches open orders for a specific trading pair.

        :param pair: The trading pair (e.g., BTCUSDT).
        :return: List of open orders as dictionaries.
        """
        return self.api_client.get_open_orders(pair)

    def place_order(self, order_details):
        """
        Places a new order.

        :param order_details: Dictionary containing order details.
        :return: API response.
        """
        self.logger.warning(f"Failed to place order. Place order function are disabled.")
        return None
        #return self.api_client.place_order(order_details)

    def get_account_balances(self):
        """
        Fetches the user's current account balances.

        :return: Dictionary with asset names as keys and balances as values.
        """
        return self.api_client.get_account_balances()

    def get_symbol_info(self, symbol, api_name=None):
        """
        Fetches symbol information from the current API.

        :param symbol: The asset symbol.
        :return: SymbolInfo object containing name, exchange, and symbol.
        """
        if(api_name):
            if api_name not in self.api_clients:
                raise ValueError(f"Unsupported API: {api_name}")
            else:
                return self.api_clients[api_name].get_symbol_info(symbol)
        else:
            return self.api_client.get_symbol_info(symbol)
    



