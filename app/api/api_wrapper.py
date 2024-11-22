from app.api.binance_api import BinanceAPI
import logging

class APIWrapper:
    def __init__(self, api_name="binance"):
        self.logger = logging.getLogger(__name__)
        
        # Select the API based on the api_name argument
        if api_name == "binance":
            self.api = BinanceAPI()
        else:
            raise ValueError(f"API {api_name} is not supported.")
        
        self.logger.info(f"API initialized: {api_name}")

    def get_trading_pairs(self):
        """Fetch trading pairs using the selected API."""
        return self.api.get_trading_pairs()

    def get_candlestick_data(self, trading_pair, interval='1h'):
        """Fetch candlestick data using the selected API."""
        return self.api.get_candlestick_data(trading_pair, interval)

    def get_depth_data(self, trading_pair):
        """Fetch depth data using the selected API."""
        return self.api.get_depth_data(trading_pair)
