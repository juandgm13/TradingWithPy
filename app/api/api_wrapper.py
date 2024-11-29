from binance.spot import Spot
from app.utils.logger import setup_logger

class APIWrapper:
    def __init__(self, api_key=None, api_secret=None, api_name="binance"):
        """
        Initialize the API wrapper.
        :param api_key: Binance API key (optional)
        :param api_secret: Binance API secret (optional)
        :param api_name: The name of the API, default is "binance"
        """
        self.logger = setup_logger()
        
        # Initialize the Binance client
        if api_name == "binance":
            self.client = Spot(api_key=api_key, api_secret=api_secret)
        else:
            raise ValueError(f"Unsupported API: {api_name}")
        
        self.logger.info(f"APIWrapper initialized with {api_name} API.")

    def get_trading_pairs(self):
        """
        Fetches all available trading pairs (symbols) from Binance.
        :return: List of trading pairs as strings.
        """
        try:
            exchange_info = self.client.exchange_info()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
            self.logger.debug(f"Fetched trading pairs: {symbols}")
            return symbols
        except Exception as e:
            self.logger.error(f"Error fetching trading pairs: {e}")
            raise

    def get_candlestick_data(self, trading_pair, interval='1h', limit=100):
        """
        Fetches candlestick data for a given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param interval: Candlestick interval (default: '1h').
        :param limit: Number of candlesticks to fetch (default: 100).
        :return: List of candlestick data.
        """
        try:
            candlesticks = self.client.klines(trading_pair, interval, limit=limit)
            self.logger.debug(f"Fetched candlestick data for {trading_pair}: {candlesticks}")
            return candlesticks
        except Exception as e:
            self.logger.error(f"Error fetching candlestick data for {trading_pair}: {e}")
            raise

    def get_depth_data(self, trading_pair, limit=100):
        """
        Fetches depth data for a given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :param limit: Number of levels to fetch (default: 100).
        :return: Depth data (bids and asks).
        """
        try:
            depth = self.client.depth(trading_pair, limit=limit)
            self.logger.debug(f"Fetched depth data for {trading_pair}: {depth}")
            return depth
        except Exception as e:
            self.logger.error(f"Error fetching depth data for {trading_pair}: {e}")
            raise

    def get_ticker_info(self, trading_pair):
        """
        Fetches ticker information for the given trading pair.
        :param trading_pair: The trading pair (e.g., BTCUSDT).
        :return: A dictionary containing price, change, high, low, and volume.
        """
        try:
            # Fetch current price
            price = self.client.ticker_price(trading_pair)
            # Fetch 24-hour statistics
            stats = self.client.ticker_24hr(trading_pair)
            
            # Prepare the result dictionary
            ticker_info = {
                'price': float(price['price']),
                'change': float(stats['priceChangePercent']),
                'high': float(stats['highPrice']),
                'low': float(stats['lowPrice']),
                'volume': float(stats['volume'])
            }

            self.logger.debug(f"Fetched ticker info for {trading_pair}: {ticker_info}")
            return ticker_info

        except Exception as e:
            self.logger.error(f"Error fetching ticker info for {trading_pair}: {e}")
            raise
