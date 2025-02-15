
class IndicatorCalculator:
    """A class dedicated to calculating technical indicators using candlestick data."""

    @staticmethod
    def extract_closing_prices(candlesticks):
        """Extracts closing prices from candlestick data."""
        return [float(c["close"]) for c in candlesticks]

    @staticmethod
    def calculate_sma(period, candlesticks):
        """Calculate Simple Moving Average (SMA)."""
        closing_prices = IndicatorCalculator.extract_closing_prices(candlesticks)
        return [sum(closing_prices[i - period:i]) / period for i in range(period, len(closing_prices))]

    @staticmethod
    def calculate_ema(period, candlesticks):
        """Calculate Exponential Moving Average (EMA)."""
        closing_prices = IndicatorCalculator.extract_closing_prices(candlesticks)
        ema = [None] * (period - 1)  # None values for early indices
        multiplier = 2 / (period + 1)
        initial_sma = sum(closing_prices[:period]) / period
        ema.append(initial_sma)

        for i in range(period, len(closing_prices)):
            new_ema = (closing_prices[i] - ema[-1]) * multiplier + ema[-1]
            ema.append(new_ema)
        return ema

    @staticmethod
    def calculate_bollinger_bands(period, std_dev_multiplier, candlesticks):
        """Calculate Bollinger Bands."""
        # Extraer los precios de cierre de los candlesticks
        closing_prices = IndicatorCalculator.extract_closing_prices(candlesticks)
        
        # Verificar si la longitud de los precios de cierre es menor que el período
        if len(closing_prices) < period:
            raise ValueError(f"La longitud de los datos ({len(closing_prices)}) es menor que el período especificado ({period}).")
        
        # Calcular la Media Móvil Simple (SMA)
        sma = IndicatorCalculator.calculate_sma(period, candlesticks)

        # Verificar que la SMA tenga la longitud adecuada
        if len(sma) < period:
            raise ValueError(f"La longitud de la SMA calculada es demasiado corta. Longitud: {len(sma)}, Período: {period}")

        # Calcular las desviaciones estándar para cada valor en los precios de cierre
        std_devs = []
        for i in range(len(closing_prices)):
            if i >= (period):
                # Obtener los últimos 'period' precios de cierre
                window = closing_prices[i - period + 1:i + 1]  
                mean = sum(window) / period
                variance = sum((x - mean) ** 2 for x in window) / period
                std_dev = variance ** 0.5
                std_devs.append(std_dev)

        # Calcular las bandas superior e inferior de Bollinger
        upper_band = []
        lower_band = []
        for i in range(len(sma)):
            if sma[i] is not None and std_devs[i] is not None:  # Asegurarse de que ambos sean números válidos
                upper_band.append(sma[i] + std_dev_multiplier * std_devs[i])
                lower_band.append(sma[i] - std_dev_multiplier * std_devs[i])
            else:
                upper_band.append(None)  # No se puede calcular si no hay datos
                lower_band.append(None)

        return upper_band, lower_band



