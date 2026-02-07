
from app.utils.logger import setup_logger
from abc import ABC, abstractmethod
from app.utils.indicators import IndicatorCalculator

class Strategy_class(ABC):
    @abstractmethod
    def execute(self):
        pass

class ThreeScreenStrategy(Strategy_class):
    # Three Screens Trading Method - Developed by Alexander Elder
    #   This strategy analyzes the market using three different timeframes 
    #   to filter out false signals and improve trade accuracy.

    # 1st Screen: Long-Term Trend (Macro Analysis)
    # - Uses a higher timeframe (e.g., daily or weekly chart).
    # - Identifies the overall trend using:
    #   - MACD (12,26,9): 
    #       - Bullish trend if MACD line > Signal line.
    #       - Bearish trend if MACD line < Signal line.
    #   - 50 and 200-period EMA: 
    #       - Bullish if EMA 50 > EMA 200 (Golden Cross).
    #       - Bearish if EMA 50 < EMA 200 (Death Cross).
    # - Objective:
    #   - If bullish trend → Only look for long (buy) opportunities.
    #   - If bearish trend → Only look for short (sell) opportunities.
    #   - If trend is unclear → Avoid trading.

    # 2nd Screen: Correction and Momentum (Intermediate Timeframe)
    # - Uses a medium timeframe (e.g., 4-hour chart if the first screen is daily).
    # - Detects retracements within the trend using:
    #   - RSI (14):
    #       - Oversold (<30) → Potential buy signal in an uptrend.
    #       - Overbought (>70) → Potential sell signal in a downtrend.
    #   - Bollinger Bands:
    #       - If price touches the lower band in an uptrend → Possible entry.
    #       - If price touches the upper band in a downtrend → Possible short.
    # - Objective:
    #   - If trend is bullish → Wait for price to pull back to oversold RSI or lower Bollinger Band.
    #   - If trend is bearish → Wait for price to rise to overbought RSI or upper Bollinger Band.
    #   - If RSI is neutral (30-70) and bands are not hit → Stay out.

    # 3rd Screen: Entry Execution (Lower Timeframe)
    # - Uses a lower timeframe (e.g., 1-hour or 15-minute chart).
    # - Searches for precise entry signals, such as:
    #   - Candlestick patterns (Engulfing, Hammer, Doji, etc.).
    #   - Short-term moving average crossovers (e.g., EMA 9 crosses above EMA 21 for a buy).
    #   - Volume increase → Confirms the breakout or reversal.
    # - Objective:
    #   - If price forms a bullish candlestick (e.g., bullish engulfing) near support → Enter long.
    #   - If price forms a bearish candlestick (e.g., shooting star) near resistance → Enter short.
    #   - If volume is low or pattern is unclear → Avoid trade.

    # Example:
    # - Screen 1 (Daily): BTC is in an uptrend (MACD positive, EMA 50 > EMA 200).
    # - Screen 2 (4H): BTC is pulling back, RSI ~30 (oversold), lower Bollinger Band touched.
    # - Screen 3 (1H or 15m): A bullish engulfing candle appears with volume increase.
    # - Action: Buy with stop-loss below recent low.

    def __init__(self, api_manager, api_name, long_term_interval, mid_term_interval, short_term_interval, exchange=None, logger=None):
        self.api_manager = api_manager
        self.api_name = api_name
        self.exchange = exchange
        self.long_term = long_term_interval
        self.mid_term = mid_term_interval
        self.short_term = short_term_interval

        self.logger = logger if logger else setup_logger()
        full_symbols_list = [self.api_manager.get_symbol_info(symbol, api_name) for symbol in self.api_manager.get_trading_symbols()]

        if exchange:
            self.symbols_list = [symbol for symbol in full_symbols_list if symbol.exchange == exchange]
        else:
            self.symbols_list = full_symbols_list
        
        self.state = {symbol.symbol: 'neutral' for symbol in full_symbols_list}

    def execute(self, api_manager):
        self.logger.info("Executing Three-Screen Strategy.")
        signal_changes = []
        for symbol in self.symbols_list:

            market_data = {
                self.long_term: api_manager.get_candlestick_data(symbol.symbol, interval=self.long_term, limit=250),
                self.mid_term: api_manager.get_candlestick_data(symbol.symbol, interval=self.mid_term, limit=50),
                self.short_term: api_manager.get_candlestick_data(symbol.symbol, interval=self.short_term, limit=50)
            }

            long_signal = self.analyze_long_term(market_data.get(self.long_term))
            mid_signal = self.analyze_mid_term(market_data.get(self.mid_term))
            short_signal = self.analyze_short_term(market_data.get(self.short_term))

            prev_state = self.state.get(symbol.symbol)
            new_state = prev_state  # Initialize to prevent UnboundLocalError

            if long_signal == 'buy': #bullish trend, only buy
                if prev_state == 'buy':
                    # to close the position
                    if mid_signal == 'sell':
                        if short_signal == 'sell':
                            new_state = 'sell'
                else:
                    # to open new long position
                    if mid_signal == 'buy':
                        if short_signal == 'buy':
                            new_state = 'buy'
            elif long_signal == 'sell': #bearish trend, only sell
                if prev_state == 'sell':
                    # to close the position
                    if mid_signal == 'buy':
                        if short_signal == 'buy':
                            new_state = 'buy'
                else:
                    # to open new short position
                    if mid_signal == 'sell':
                        if short_signal == 'sell':
                            new_state = 'sell'

            if new_state != prev_state:
                self.state[symbol.symbol] = new_state
                if new_state in ['buy', 'sell']:
                    self.logger.info(f"Three-screen strategy triggered a {new_state.upper()} signal for {symbol}.")
                    signal_changes.append({
                        'symbol': symbol,
                        'type': new_state,
                        'details': f"Three-screen strategy triggered a {new_state.upper()} signal.",
                        'market_data': market_data
                    })

        if signal_changes:
            self.logger.info(f"Signals generated: {signal_changes}")
        else:
            self.logger.info("No valid signal generated.")

        return signal_changes
  
    def analyze_long_term(self, data):
        calculator = IndicatorCalculator()
        closing_prices = calculator.extract_closing_prices(data)

        # Get MACD values
        macd_line, signal_line, _ = calculator.calculate_macd(closing_prices, 12, 26, 9)

        # Get EMAs
        ema_50 = calculator.calculate_ema(50, closing_prices)[-1]  # Last value of EMA 50
        ema_200 = calculator.calculate_ema(200, closing_prices)[-1]  # Last value of EMA 200

        # Determine trend
        if macd_line[-1] > signal_line[-1] and ema_50 > ema_200:
            return 'buy'
        elif macd_line[-1] < signal_line[-1] and ema_50 < ema_200:
            return 'sell'
        
        return 'neutral'

    def analyze_mid_term(self, data):
        calculator = IndicatorCalculator()
        closing_prices = calculator.extract_closing_prices(data)

        rsi = calculator.calculate_rsi(14, closing_prices)
        std_dev_multiplier = 2
        upper_band, lower_band = calculator.calculate_bollinger_bands(20, std_dev_multiplier, closing_prices)

        if rsi[-1] < 30 or closing_prices[-1] < lower_band[-1]:
            return 'buy'
        elif rsi[-1] > 70 or closing_prices[-1] > upper_band[-1]:
            return 'sell'
        return 'neutral'

    def analyze_short_term(self, data):
        calculator = IndicatorCalculator()
        closing_prices = calculator.extract_closing_prices(data)
        ema_9 = calculator.calculate_ema(9, closing_prices)
        ema_21 = calculator.calculate_ema(21, closing_prices)
        if ema_9[-1] > ema_21[-1]:
            return 'buy'
        elif ema_9[-1] < ema_21[-1]:
            return 'sell'
        return 'neutral'
