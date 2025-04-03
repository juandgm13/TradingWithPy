from alpaca_trade_api.rest import REST, TimeFrame,Sort
from app.utils.logger import setup_logger
from datetime import datetime, timedelta
import pandas as pd
from app.utils.symbol_info import SymbolInfo

# API documentation: https://docs.alpaca.markets/reference/authentication-2

class AlpacaAPI:
    def __init__(self, api_key, api_secret, logger=None, test_enabled=False, stock=True):
        """
        Initialize the Alpaca API wrapper.
        :param api_key: Alpaca API key.
        :param api_secret: Alpaca API secret.
        :param logger: Initialized logger (optional).
        :param test_enabled: to use paper (optional).
        :param stock: to use stock or crypto assets (optional).
        """
        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger

        self.assets_type="stock" if stock else "crypto"

        if test_enabled:
            self.client = REST(api_key, api_secret, "https://paper-api.alpaca.markets")
            self.logger.info("AlpacaAPI initialized (paper version).")
        else:
            self.client = REST(api_key, api_secret, "https://api.alpaca.markets")
            self.logger.info("AlpacaAPI initialized.")

    def get_trading_symbols(self):
        """
        Fetches all available tradable assets filtered by asset type.

        :return: List of tradable symbols.
        """
        try:
            # Fetch all active assets
            assets = self.client.list_assets(status="active")

            # Map 'stock' to 'us_equity' for Alpaca's API
            asset_class = "us_equity" if self.assets_type == "stock" else "crypto"

            # Filter assets by the determined asset_class
            filtered_assets = [asset for asset in assets if asset._raw.get("class") == asset_class and asset._raw.get("tradable")]

            # Extract symbols
            symbols = [asset.symbol for asset in filtered_assets]

            self.logger.debug(f"Fetched tradable symbols for {self.assets_type}: {symbols}")
            return symbols
        except Exception as e:
            self.logger.error(f"Error fetching trading symbols for {self.assets_type}: {e}")
            raise

    def get_candlestick_data(self, symbol, interval='1h', limit=100, extra_time=10):
        """
        Fetches candlestick data for a given symbol.
        :param symbol: The symbol (e.g., AAPL).
        :param interval: Candlestick interval (default: '1h').
        :param limit: Number of candlesticks to fetch (default: 100).
        :param extra_time: Extra time range multiplier to ensure sufficient data.
        :return: List of candlestick data as dictionaries.
        """
        try:
            # Map intervals to Alpaca's format
            interval_map = {'1d': '1D', '4h': '4H', '1h': '1H', '15m': '15Min'}
            AlpacaTimeFrame = interval_map.get(interval, '1H')

            # Calculate start time
            now = datetime.now()
            time_deltas = {
                '1d': timedelta(days=limit * extra_time),
                '4h': timedelta(hours=4 * limit * extra_time),
                '1h': timedelta(hours=limit * extra_time),
                '15m': timedelta(minutes=15 * limit * extra_time)
            }
            start = now - time_deltas.get(interval, timedelta(hours=limit * extra_time))

            # Format start time
            start_time_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Fetch data based on asset type
            if self.assets_type == "stock":
                barset = self.client.get_bars(symbol, AlpacaTimeFrame, start=start_time_str)
            else:
                barset = self.client.get_crypto_bars(symbol, AlpacaTimeFrame, start=start_time_str)

            # Convert bars to a structured list of dictionaries
            candlestick_data = [
                {
                    "time": int(pd.to_datetime(bar.t).timestamp()),  # timestamp to int
                    "open": float(bar.o),  # Open price
                    "high": float(bar.h),  # High price
                    "low": float(bar.l),  # Low price
                    "close": float(bar.c),  # Close price
                    "volume": float(bar.v)  # Volume
                }
                for bar in barset
            ]

            # Ensure sufficient data, recursively fetch more if needed
            if len(candlestick_data) < limit and extra_time < 500:
                return self.get_candlestick_data(symbol, interval, limit, extra_time + 30)

            # Sort by time and trim to the exact limit
            candlestick_data.sort(key=lambda x: x["time"])
            candlestick_data = candlestick_data[-limit:]

            self.logger.debug(f"Fetched candlestick data for {symbol}: {candlestick_data}")
            return candlestick_data

        except Exception as e:
            self.logger.error(f"Error fetching candlestick data for {symbol}: {e}")
            raise

    def get_depth_data(self, symbol, limit=100):
        """
        Fetches the latest order book for a given symbol.
        :param symbol: The symbol (e.g., AAPL).
        :return: Order book data.
        """
        return None # not available for this api

    def get_ticker_info(self, symbol):
        """
        Fetches the latest price information for the given symbol.
        :param symbol: The symbol (e.g., AAPL).
        :return: A dictionary containing price, high, low, and volume.
        """
        try:
            if self.assets_type == "stock":
                snapshot = self.client.get_snapshot(symbol)
                ticker_info = {
                    "price": snapshot.latest_trade.p,
                    "high": snapshot.daily_bar.h,
                    "low": snapshot.daily_bar.l,
                    "volume": snapshot.daily_bar.v
                }
            else:
                snapshot = self.client.get_crypto_snapshot(symbol)
                ticker_info = {
                    "price": snapshot[symbol].latest_trade.p,
                    "high": snapshot[symbol].daily_bar.h,
                    "low": snapshot[symbol].daily_bar.l,
                    "volume": snapshot[symbol].daily_bar.v
                }

            self.logger.debug(f"Fetched ticker info for {symbol}: {ticker_info}")
            return ticker_info
        except Exception as e:
            self.logger.error(f"Error fetching ticker info for {symbol}: {e}")
            raise

    def get_account_balances(self):
        """
        Fetches the account balances.
        :return: A dictionary of account balances.
        """
        try:
            account = self.client.get_account()
            balances = {
                "cash": account.cash,
                "buying_power": account.buying_power,
            }
            self.logger.debug(f"Fetched account balances: {balances}")
            return balances
        except Exception as e:
            self.logger.error(f"Error fetching account balances: {e}")
            raise
    
    def place_order(self, symbol, qty, side, order_type="market", time_in_force="gtc", limit_price=None, stop_price=None):
        """
        Places a new order.
        :param symbol: The trading symbol (e.g., AAPL).
        :param qty: Quantity to buy/sell.
        :param side: 'buy' or 'sell'.
        :param order_type: Order type ('market', 'limit', or 'stop').
        :param time_in_force: Time in force (default: 'gtc').
        :param limit_price: Limit price (for limit orders).
        :param stop_price: Stop price (for stop orders).
        :return: The response from Alpaca API containing order details.
        """
        try:
            order = self.client.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price,
            )
            self.logger.info(f"Placed order: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            raise

    def get_open_orders(self, symbol=None):
        """
        Fetch open orders for a specific symbol or all symbols if no symbol is specified.
        :param symbol: (optional) The symbol (e.g., AAPL). If None, fetches all open orders.
        :return: List of open orders as dictionaries.
        """
        try:
            # Fetch all open orders from Alpaca
            open_orders = self.client.list_orders(status='open', symbols=[symbol] if symbol else None)

            # Process the order data into a list of dictionaries
            orders_list = [{
                'id': order.id,
                'symbol': order.symbol,
                'qty': order.qty,
                'filled_qty': order.filled_qty,
                'type': order.order_type,
                'side': order.side,
                'status': order.status,
                'limit_price': order.limit_price,
                'stop_price': order.stop_price,
                'submitted_at': order.submitted_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
            } for order in open_orders]

            self.logger.info(f"Fetched {len(orders_list)} open orders for symbol: {symbol if symbol else 'all symbols'}.")
            return orders_list
        except Exception as e:
            self.logger.error(f"Error fetching open orders for symbol {symbol}: {e}")
            raise

    def get_symbol_info(self, symbol: str):
        """
        Fetches symbol information from Alpaca.

        :param symbol: The asset symbol (e.g., 'AAPL').
        :return: SymbolInfo object containing name, exchange, and symbol.
        """
        try:
            asset = self.client.get_asset(symbol)
            name = asset.name if hasattr(asset, "name") else symbol
            exchange = asset.exchange if hasattr(asset, "exchange") else "Alpaca"
            
            return SymbolInfo(name=name, exchange=exchange, symbol=symbol)

        except Exception as e:
            self.logger.error(f"Error fetching symbol info from Alpaca for {symbol}: {e}")
            raise
