

class SymbolInfo:
    def __init__(self, name: str, exchange: str, symbol: str):
        """
        Initializes the SymbolInfo class.

        :param name: The name of the asset (e.g., "Apple Inc." or "Bitcoin").
        :param exchange: The exchange where the asset is traded (e.g., "NASDAQ" or "BINANCE").
        :param symbol: The trading symbol (e.g., "AAPL" or "BTC/USD").
        """
        self.name = name
        self.exchange = exchange
        self.symbol = symbol

    def __repr__(self):
        return f"SymbolInfo(name='{self.name}', exchange='{self.exchange}', symbol='{self.symbol}')"

    def to_dict(self):
        """
        Converts the SymbolInfo object into a dictionary.
        """
        return {"name": self.name, "exchange": self.exchange, "symbol": self.symbol}
