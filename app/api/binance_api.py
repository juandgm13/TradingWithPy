from binance.spot import Spot
from app.utils.logger import setup_logger

class BinanceAPI:
    def __init__(self, api_key=None, api_secret=None, logger=None, test_enabled=False):
        """
        Initialize the Binance API wrapper.
        :param api_key: Binance API key (optional)
        :param api_secret: Binance API secret (optional)
        :param logger: Initialized logger (optional)
        """
        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger
        
        if test_enabled:
            self.client = Spot(api_key=api_key, api_secret=api_secret, base_url="https://testnet.binance.vision")
            self.logger.info("BinanceAPI initialized (TestNET).")
        else:
            self.client = Spot(api_key=api_key, api_secret=api_secret)
            self.logger.info("BinanceAPI initialized.")

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

    def get_open_orders(self, pair):
        """
        Fetch open orders for a specific trading pair.

        Args:
            pair (str): The trading pair, e.g., 'BTCUSDT'.

        Returns:
            list: A list of open orders as dictionaries.
        """
        try:
            open_orders = self.client.get_open_orders(symbol=pair)
            self.logger.info(f"Fetched {len(open_orders)} open orders for {pair}.")
            return open_orders
        except Exception as e:
            self.logger.error(f"Failed to fetch open orders for {pair}: {str(e)}")
            raise e

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
        try:
            response = self.client.new_order(
                symbol=order_details['symbol'],
                side=order_details['side'],
                type=order_details['type'],
                timeInForce='GTC',  # Good-Till-Canceled
                quantity=order_details['quantity'],
                price=order_details['price']
            )
            self.logger.info(f"Placed order: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place order: {str(e)}")
            raise e