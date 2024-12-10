import os
from app.utils.logger import setup_logger
from app.api.binance_api import BinanceAPI
from app.utils.config import ConfigLoader

class APIWrapper:
    def __init__(self, api_name="binance", logger=None):
        """
        Initialize the API wrapper.
        :param api_name: The name of the API, default is "binance"
        :param logger: Initialized logger (optional)
        """
        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger
        
        # Initialize the config loader
        config = ConfigLoader("app/utils/config/config.json")

        # Retrieve values from the configuration
        self.enable_test_trading = config.get("enable_test_trading", False)

        # Initialize the Binance client
        if api_name == "binance":
            # Fetch the API key and secret from environment variables
            if self.enable_test_trading:
                api_key = os.environ.get('BINANCE_API_KEY_TEST')
                api_secret = os.environ.get('BINANCE_API_SECRET_TEST')
            else:
                api_key = os.environ.get('BINANCE_API_KEY')
                api_secret = os.environ.get('BINANCE_API_SECRET')

            if not api_key or not api_secret:
                self.api_client = BinanceAPI(logger=self.logger)
                self.logger.warning(f"Connected with API without Key nor Secret")
            else:
                self.api_client = BinanceAPI(api_key=api_key, api_secret=api_secret, logger=self.logger, test_enabled=self.enable_test_trading)
                self.logger.info(f"Connected with API Key: {api_key} and Secret: {api_secret}")
        else:
            raise ValueError(f"Unsupported API: {api_name}")
        
        self.logger.info(f"APIWrapper initialized with {api_name} API.")

    def get_trading_pairs(self):
        """
        Fetches all available trading pairs (symbols) from current API.
        :return: List of trading pairs as strings.
        """
        return self.api_client.get_trading_pairs()
            

    def get_candlestick_data(self, trading_pair, interval='1h', limit=100):
        """
        Fetches candlestick data for a given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param interval: Candlestick interval (default: '1h').
        :param limit: Number of candlesticks to fetch (default: 100).
        :return: List of candlestick data.
        """
        return self.api_client.get_candlestick_data(trading_pair, interval, limit)

    def get_depth_data(self, trading_pair, limit=100):
        """
        Fetches depth data for a given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param limit: Number of levels to fetch (default: 100).
        :return: Depth data (bids and asks).
        """
        return self.api_client.get_depth_data(trading_pair, limit)

    def get_ticker_info(self, trading_pair):
        """
        Fetches ticker information for the given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :return: A dictionary containing price, change, high, low, and volume.
        """
        return self.api_client.get_ticker_info(trading_pair)
    
    def get_open_orders(self, pair):
        """
        Fetch open orders for a specific trading pair.

        Args:
            pair (str): The trading pair, e.g., 'BTCUSDT'.

        Returns:
            list: A list of open orders as dictionaries.
        """
        return self.api_client.get_open_orders(pair)

    def place_order(self, order_details):
        """
        Places a new limit order.

        Args:
            order_details (dict): Details of the order to be placed, including:
                                  - symbol (str): The trading pair, e.g., 'BTCUSDT'.
                                  - side (str): 'BUY' or 'SELL'.
                                  - type (str): Order type, e.g., 'LIMIT'.
                                  - price (str): The order price as a string.
                                  - quantity (str): The order quantity as a string.

        Returns:
            dict: The response from the Binance API containing order details.
        """
        return self.api_client.place_order(order_details)
