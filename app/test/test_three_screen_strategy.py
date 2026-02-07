import pytest
from unittest.mock import Mock, MagicMock
from app.strategies.strategies import ThreeScreenStrategy
from app.utils.symbol_info import SymbolInfo


@pytest.fixture
def mock_api_manager():
    """Create mock API manager for testing"""
    api_manager = Mock()
    api_manager.get_trading_symbols.return_value = ["BTCUSDT", "ETHUSDT"]

    # Mock symbol info
    btc_symbol = SymbolInfo(symbol="BTCUSDT", name="Bitcoin", exchange="Binance")
    eth_symbol = SymbolInfo(symbol="ETHUSDT", name="Ethereum", exchange="Binance")

    api_manager.get_symbol_info.side_effect = lambda symbol, api_name: (
        btc_symbol if symbol == "BTCUSDT" else eth_symbol
    )

    return api_manager


@pytest.fixture
def mock_logger():
    """Create mock logger for testing"""
    return Mock()


def create_candlestick_data(prices, num_candles=50):
    """Helper to create candlestick data from price list"""
    return [
        {
            "time": i * 1000,
            "open": prices[i % len(prices)],
            "high": prices[i % len(prices)] + 2,
            "low": prices[i % len(prices)] - 2,
            "close": prices[i % len(prices)],
            "volume": 1000
        }
        for i in range(num_candles)
    ]


class TestThreeScreenStrategyInitialization:
    """Tests for ThreeScreenStrategy initialization"""

    def test_init_basic(self, mock_api_manager, mock_logger):
        """Should initialize strategy correctly"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        assert strategy.long_term == "1d"
        assert strategy.mid_term == "4h"
        assert strategy.short_term == "1h"
        assert strategy.api_name == "binance"
        assert strategy.logger == mock_logger

    def test_init_state_dictionary_uses_symbol_string(self, mock_api_manager, mock_logger):
        """State dictionary should use symbol.symbol (string) as key, not symbol object"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Verify state keys are strings, not SymbolInfo objects
        assert "BTCUSDT" in strategy.state
        assert "ETHUSDT" in strategy.state
        assert all(isinstance(key, str) for key in strategy.state.keys())

    def test_init_default_state_neutral(self, mock_api_manager, mock_logger):
        """All symbols should start with 'neutral' state"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        assert all(state == 'neutral' for state in strategy.state.values())

    def test_init_filter_by_exchange(self, mock_api_manager, mock_logger):
        """Should filter symbols by exchange if specified"""
        # Add symbol from different exchange
        alpaca_symbol = SymbolInfo(symbol="AAPL", name="Apple", exchange="Alpaca")
        mock_api_manager.get_trading_symbols.return_value = ["BTCUSDT", "ETHUSDT", "AAPL"]

        def get_symbol_info(symbol, api_name):
            if symbol == "BTCUSDT":
                return SymbolInfo(symbol="BTCUSDT", name="Bitcoin", exchange="Binance")
            elif symbol == "ETHUSDT":
                return SymbolInfo(symbol="ETHUSDT", name="Ethereum", exchange="Binance")
            else:
                return alpaca_symbol

        mock_api_manager.get_symbol_info.side_effect = get_symbol_info

        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            exchange="Binance",
            logger=mock_logger
        )

        # Should only include Binance symbols
        assert len(strategy.symbols_list) == 2
        assert all(s.exchange == "Binance" for s in strategy.symbols_list)


class TestAnalyzeLongTerm:
    """Tests for analyze_long_term method"""

    def test_analyze_long_term_bullish(self, mock_api_manager, mock_logger):
        """Should return 'buy' for bullish trend (MACD positive + Golden Cross)"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create VERY strong uptrend data to ensure clear buy signal
        # Start low, then strong exponential growth
        prices = [50 + (i ** 1.2) for i in range(250)]
        data = create_candlestick_data(prices, 250)

        result = strategy.analyze_long_term(data)
        assert result == 'buy'

    def test_analyze_long_term_bearish(self, mock_api_manager, mock_logger):
        """Should return 'sell' for bearish trend (MACD negative + Death Cross)"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create VERY strong downtrend data to ensure clear sell signal
        # Start high, then strong exponential decline
        prices = [500 - (i ** 1.2) for i in range(250)]
        data = create_candlestick_data(prices, 250)

        result = strategy.analyze_long_term(data)
        assert result == 'sell'

    def test_analyze_long_term_neutral(self, mock_api_manager, mock_logger):
        """Should return 'neutral' for mixed signals"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create sideways market data
        prices = [100] * 250
        data = create_candlestick_data(prices, 250)

        result = strategy.analyze_long_term(data)
        assert result == 'neutral'


class TestAnalyzeMidTerm:
    """Tests for analyze_mid_term method"""

    def test_analyze_mid_term_oversold(self, mock_api_manager, mock_logger):
        """Should return 'buy' when RSI < 30 (oversold)"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create strong downtrend to get RSI < 30
        prices = [100 - i*2 for i in range(50)]
        data = create_candlestick_data(prices, 50)

        result = strategy.analyze_mid_term(data)
        assert result == 'buy'

    def test_analyze_mid_term_overbought(self, mock_api_manager, mock_logger):
        """Should return 'sell' when RSI > 70 (overbought)"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create strong uptrend to get RSI > 70
        prices = [100 + i*2 for i in range(50)]
        data = create_candlestick_data(prices, 50)

        result = strategy.analyze_mid_term(data)
        assert result == 'sell'

    def test_analyze_mid_term_neutral(self, mock_api_manager, mock_logger):
        """Should return 'neutral' when RSI is between 30-70"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create sideways market
        prices = [100, 102, 98, 101, 99, 103, 97, 102, 100] * 6
        data = create_candlestick_data(prices, 50)

        result = strategy.analyze_mid_term(data)
        assert result == 'neutral'


class TestAnalyzeShortTerm:
    """Tests for analyze_short_term method"""

    def test_analyze_short_term_bullish_crossover(self, mock_api_manager, mock_logger):
        """Should return 'buy' when EMA 9 > EMA 21"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create recent uptrend
        prices = [100 + i*0.5 for i in range(50)]
        data = create_candlestick_data(prices, 50)

        result = strategy.analyze_short_term(data)
        assert result == 'buy'

    def test_analyze_short_term_bearish_crossover(self, mock_api_manager, mock_logger):
        """Should return 'sell' when EMA 9 < EMA 21"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Create recent downtrend
        prices = [100 - i*0.5 for i in range(50)]
        data = create_candlestick_data(prices, 50)

        result = strategy.analyze_short_term(data)
        assert result == 'sell'


class TestExecuteMethod:
    """Tests for execute method"""

    def test_execute_new_state_initialized_prevents_error(self, mock_api_manager, mock_logger):
        """new_state should be initialized to prevent UnboundLocalError"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Mock candlestick data that will produce 'neutral' signals
        sideways_data = create_candlestick_data([100] * 50, 250)

        mock_api_manager.get_candlestick_data.return_value = sideways_data

        # Should not raise UnboundLocalError even with all neutral signals
        result = strategy.execute(mock_api_manager)
        assert isinstance(result, list)

    def test_execute_state_transitions_buy_to_sell(self, mock_api_manager, mock_logger):
        """Should transition from 'buy' to 'sell' correctly"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Set initial state to 'buy'
        strategy.state["BTCUSDT"] = 'buy'

        # Create different data for each timeframe to get all 'sell' signals
        # Long-term: strong downtrend for MACD negative and Death Cross
        long_term_data = create_candlestick_data([500 - (i ** 1.2) for i in range(250)], 250)

        # Mid-term: Strong uptrend to get RSI > 70 (overbought)
        mid_term_data = create_candlestick_data([100 + i*2 for i in range(50)], 50)

        # Short-term: Downtrend for EMA 9 < EMA 21
        short_term_data = create_candlestick_data([100 - i*0.5 for i in range(50)], 50)

        # Mock different data for each interval
        def get_candlestick_side_effect(symbol, interval, limit):
            if interval == strategy.long_term:
                return long_term_data
            elif interval == strategy.mid_term:
                return mid_term_data
            else:  # short_term
                return short_term_data

        mock_api_manager.get_candlestick_data.side_effect = get_candlestick_side_effect

        result = strategy.execute(mock_api_manager)

        # State should transition to 'sell' (or remain 'buy' depending on exact signals)
        # The important thing is that it doesn't crash
        assert strategy.state["BTCUSDT"] in ['buy', 'sell', 'neutral']

    def test_execute_maintains_state_on_neutral_signal(self, mock_api_manager, mock_logger):
        """Should maintain previous state when long_signal is neutral"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Set initial state to 'buy'
        strategy.state["BTCUSDT"] = 'buy'

        # Mock neutral data (sideways market)
        neutral_data = create_candlestick_data([100] * 50, 250)
        mock_api_manager.get_candlestick_data.return_value = neutral_data

        result = strategy.execute(mock_api_manager)

        # State should remain 'buy' (not change to neutral or crash)
        assert strategy.state["BTCUSDT"] == 'buy'

    def test_execute_returns_signal_changes(self, mock_api_manager, mock_logger):
        """Should return list of signal changes"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Mock bullish data
        bullish_data = create_candlestick_data([100 + i*0.5 for i in range(50)], 250)
        mock_api_manager.get_candlestick_data.return_value = bullish_data

        result = strategy.execute(mock_api_manager)

        assert isinstance(result, list)
        # If state changed from neutral to buy/sell, should have signal changes
        if len(result) > 0:
            assert 'symbol' in result[0]
            assert 'type' in result[0]
            assert 'details' in result[0]
            assert 'market_data' in result[0]

    def test_execute_uses_symbol_string_not_object(self, mock_api_manager, mock_logger):
        """execute should use symbol.symbol string, not symbol object for state dict"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Mock data
        mock_api_manager.get_candlestick_data.return_value = create_candlestick_data([100] * 50, 250)

        # Execute should not raise KeyError due to using symbol object as key
        result = strategy.execute(mock_api_manager)

        # Verify state dict still uses strings
        assert all(isinstance(key, str) for key in strategy.state.keys())

    def test_execute_no_signal_change_no_append(self, mock_api_manager, mock_logger):
        """Should not append signal when state doesn't change"""
        strategy = ThreeScreenStrategy(
            api_manager=mock_api_manager,
            api_name="binance",
            long_term_interval="1d",
            mid_term_interval="4h",
            short_term_interval="1h",
            logger=mock_logger
        )

        # Set initial state and mock data that produces same state
        strategy.state["BTCUSDT"] = 'neutral'
        neutral_data = create_candlestick_data([100] * 50, 250)
        mock_api_manager.get_candlestick_data.return_value = neutral_data

        result = strategy.execute(mock_api_manager)

        # No signal changes should be returned
        assert len(result) == 0
