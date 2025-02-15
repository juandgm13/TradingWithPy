import pytest
from app.api.api_manager import APIManager


@pytest.fixture
def api_manager():
    """Fixture to create an APIManager instance."""
    return APIManager()

@pytest.mark.parametrize("api_name", ["binance", "alpaca-stock", "alpaca-crypto"])
def test_api_switching(api_manager, api_name):
    """Test switching between APIs."""
    api_manager.set_api(api_name)
    assert api_manager.api_name == api_name
    assert api_manager.api_client is not None

@pytest.mark.parametrize("api_name", ["binance", "alpaca-stock", "alpaca-crypto"])
def test_trading_symbols(api_manager, api_name):
    """Test that all APIs return trading symbols in list format."""
    api_manager.set_api(api_name)
    symbols = api_manager.get_trading_symbols()
    assert isinstance(symbols, list)
    assert all(isinstance(symbol, str) for symbol in symbols)  # Ensure all are strings


# Define different symbols for each API
symbols = {
    "binance": "BTCUSDT",
    "alpaca-stock": "AAPL",
    "alpaca-crypto": "ETH/USD"
}

@pytest.mark.parametrize("api_name,symbol", symbols.items())
def test_candlestick_data(api_manager, api_name, symbol):
    """Test that all APIs return candlestick data in a consistent format with different symbols."""
    api_manager.set_api(api_name)
    data = api_manager.get_candlestick_data(symbol, interval="1h", limit=10)

    assert isinstance(data, list)
    assert len(data) == 10  # Ensure all data (limit) is returned

    # Validate the structure of each candlestick entry
    required_keys = {"time", "open", "high", "low", "close", "volume"}
    
    for candle in data:
        assert isinstance(candle, dict)  # Each candlestick should be a dictionary
        assert required_keys.issubset(candle.keys())  # Ensure all required keys exist
        
        # Validate data types
        assert isinstance(candle["time"], (int, float))  # Time should be a timestamp
        assert isinstance(candle["open"], (int, float))
        assert isinstance(candle["high"], (int, float))
        assert isinstance(candle["low"], (int, float))
        assert isinstance(candle["close"], (int, float))
        assert isinstance(candle["volume"], (int, float))  # Volume should be numeric


@pytest.mark.parametrize("api_name,symbol", symbols.items())
def test_ticker_info(api_manager, api_name, symbol):
    """Test that all APIs return ticker information in dictionary format."""
    api_manager.set_api(api_name)
    ticker = api_manager.get_ticker_info(symbol)

    # Validate the structure of each candlestick entry
    required_keys = {"price", "high", "low", "volume"}

    assert isinstance(ticker, dict)
    assert required_keys.issubset(ticker.keys())  # Ensure all required keys exist
    assert isinstance(ticker["price"], (int, float))
    assert isinstance(ticker["high"], (int, float))
    assert isinstance(ticker["low"], (int, float))
    assert isinstance(ticker["volume"], (int, float))

@pytest.mark.parametrize("api_name", ["binance", "alpaca-stock", "alpaca-crypto"])
def test_account_balances(api_manager, api_name):
    """Test that all APIs return account balances in dictionary format."""
    api_manager.set_api(api_name)
    balances = api_manager.get_account_balances()

    assert isinstance(balances, dict)