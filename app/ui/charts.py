from PyQt5.QtWidgets import QVBoxLayout, QWidget, QGraphicsRectItem
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from app.utils.indicators import IndicatorCalculator
import datetime


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        """Convert timestamp values into human-readable date strings."""
        return [datetime.datetime.fromtimestamp(value/1000).strftime("%Y-%m-%d %H:%M") for value in values]
    

class CandlestickChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        # Create the chart with the custom time axis
        self.chart = pg.PlotWidget(title="Candlestick Chart", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.chart.setLabel('bottom', 'Time')
        self.chart.setLabel('left', 'Price')
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, candlestick_data, period=0, sma_enabled=False, ema_enabled=False, bb_enabled=False):
        """Updates the chart with standard candlestick format and time-based X-axis."""
        self.chart.clear()

        # Add indicators if enabled
        times = [c[0] for c in candlestick_data]
        times=times[period:]
        if(sma_enabled):
            self.add_sma(period, candlestick_data, times)
        if(ema_enabled):
            self.add_ema(period, candlestick_data, times)
        if(bb_enabled):
            self.add_bollinger_bands(period, data=candlestick_data, times=times)

        # Discard the period candlesticks if specified
        candlestick_data = candlestick_data[period:]
        
        # Extract data
        times = [c[0] for c in candlestick_data]
        opens = [float(c[1]) for c in candlestick_data]
        highs = [float(c[2]) for c in candlestick_data]
        lows = [float(c[3]) for c in candlestick_data]
        closes = [float(c[4]) for c in candlestick_data]

        # Bar width (90% of the interval between candlesticks)
        if len(times) > 1:
            bar_width = (times[1] - times[0]) * 0.9
        else:
            bar_width = 1  # Default width for single candlestick

        for t, o, h, l, c in zip(times, opens, highs, lows, closes):
            # Determine color
            is_rising = c >= o
            color = (0, 255, 0) if is_rising else (255, 0, 0)

            # Draw high-low line
            self.chart.plot([t, t], [l, h], pen=pg.mkPen(color, width=1))

            # Draw body
            body_bottom = min(o, c)
            body_top = max(o, c)
            body = QGraphicsRectItem(t - bar_width / 2, body_bottom, bar_width, body_top - body_bottom)
            body.setBrush(pg.mkBrush(color))
            body.setPen(pg.mkPen(color))
            self.chart.addItem(body)

        # Adjust the chart's scale
        if times and highs and lows:
            self.chart.setXRange(min(times), max(times), padding=0.1)
            self.chart.setYRange(min(lows), max(highs), padding=0.1)

    def add_sma(self, period=20, data=None, times=None):
        """Calculate and plot the Simple Moving Average."""
        sma_data = IndicatorCalculator.calculate_sma(period=period, candlesticks=data)
        self.chart.plot(times, sma_data, pen=pg.mkPen('blue', width=1), name="SMA")

    def add_ema(self, period=20, data=None, times=None):
        """Calculate and plot the Exponential Moving Average."""
        ema_data = IndicatorCalculator.calculate_ema(period, data)
        self.chart.plot(times, ema_data[period:], pen=pg.mkPen('orange', width=1), name="EMA")
    
    def add_bollinger_bands(self, period=20, std_dev_multiplier=2, data=None, times=None):
        """Calculate and plot Bollinger Bands."""
        upper_band, lower_band = IndicatorCalculator.calculate_bollinger_bands(period, std_dev_multiplier, data)
        # Plot the upper band in green
        self.chart.plot(times, upper_band, pen=pg.mkPen('green', width=1), name="Upper Band")
        # Plot the lower band in red
        self.chart.plot(times, lower_band, pen=pg.mkPen('red', width=1), name="Lower Band")

   


class VolumeChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Volume Chart", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.chart.setLabel('bottom', 'Time')
        self.chart.setLabel('left', 'Volume')
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, candlestick_data, discard_first_n=0):
        """Updates the volume chart with bars using distinct colors for buy/sell and adjusts scale."""
        self.chart.clear()

        # Discard the first n candlesticks if specified
        candlestick_data = candlestick_data[discard_first_n:]

        # Extract data
        times = [c[0] for c in candlestick_data]  # Timestamps
        volumes = [float(c[5]) for c in candlestick_data]  # Volumes
        is_buy_volume = [float(c[4]) >= float(c[1]) for c in candlestick_data]  # Buy/Sell distinction

        # Adjust width: use the time difference between consecutive candlesticks
        if len(times) > 1:
            bar_width = (times[1] - times[0]) * 0.9  # Slightly narrower than the time difference
        else:
            bar_width = 1  # Default if only one candlestick

        # Create brushes for colors (green for buy, red for sell)
        brushes = [
            pg.mkBrush(0, 255, 0, 150) if buy else pg.mkBrush(255, 0, 0, 150)
            for buy in is_buy_volume
        ]

        # Plot bars
        bars = pg.BarGraphItem(x=times, height=volumes, width=bar_width, brushes=brushes)
        self.chart.addItem(bars)

        # Adjust the chart's scale
        if times and volumes:
            self.chart.setXRange(min(times), max(times), padding=0.1)
            self.chart.setYRange(0, max(volumes) * 1.1, padding=0.1)



class DepthChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Depth Chart")
        self.chart.setLabel('bottom', 'Price')
        self.chart.setLabel('left', 'Cumulative Volume')
        self.chart.addLegend()
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, depth_data, discard_first_n=0):
        """Updates the depth chart with cumulative data and adjusts scale."""
        self.chart.clear()

       # Discard the first n entries from bids and asks
        bids = sorted(depth_data['bids'][discard_first_n:], key=lambda x: float(x[0]), reverse=True)
        asks = sorted(depth_data['asks'][discard_first_n:], key=lambda x: float(x[0]))

        # Extract and sort data
        bids = sorted(depth_data['bids'], key=lambda x: float(x[0]), reverse=True)  # Descending prices
        asks = sorted(depth_data['asks'], key=lambda x: float(x[0]))  # Ascending prices

        bid_prices = [float(b[0]) for b in bids]
        bid_volumes = [float(b[1]) for b in bids]
        ask_prices = [float(a[0]) for a in asks]
        ask_volumes = [float(a[1]) for a in asks]

        # Calculate cumulative volumes
        cumulative_bid_volumes = [sum(bid_volumes[:i + 1]) for i in range(len(bid_volumes))]
        cumulative_ask_volumes = [sum(ask_volumes[:i + 1]) for i in range(len(ask_volumes))]

        # Plot bids
        bid_plot = self.chart.plot(
            bid_prices,
            cumulative_bid_volumes,
            pen=pg.mkPen('g', width=2),
            fillLevel=0,
            brush=(50, 200, 50, 100),
            name="Bids"
        )

        # Plot asks
        ask_plot = self.chart.plot(
            ask_prices,
            cumulative_ask_volumes,
            pen=pg.mkPen('r', width=2),
            fillLevel=0,
            brush=(200, 50, 50, 100),
            name="Asks"
        )

        # Adjust the chart's scale
        all_prices = bid_prices + ask_prices
        all_volumes = cumulative_bid_volumes + cumulative_ask_volumes
        if all_prices and all_volumes:
            self.chart.setXRange(min(all_prices), max(all_prices), padding=0.1)
            self.chart.setYRange(0, max(all_volumes) * 1.1, padding=0.1)


class RSIChart(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = pg.PlotWidget(title="Relative Strength Index (RSI)")
        self.chart.setLabel('left', 'RSI')
        self.chart.setLabel('bottom', 'Time')

        layout = QVBoxLayout()
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, data, period=14):
        # Calculate RSI from the price data
        rsi = self.__calculate_rsi(data, period)

        # Plot the RSI data
        self.chart.clear()  # Clear the previous plot
        self.chart.plot(rsi, pen=pg.mkPen('purple', width=2), name=f'RSI ({period})')

        # Add overbought (70) and oversold (30) lines
        self.chart.addLine(y=70, pen=pg.mkPen('red', width=1, style=Qt.DashLine))  # Overbought line
        self.chart.addLine(y=30, pen=pg.mkPen('green', width=1, style=Qt.DashLine))  # Oversold line

    def __calculate_rsi(self, data, period=14):
        gains = []
        losses = []

        for i in range(1, len(data)):
            change = data[i] - data[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        # Calculate average gain and loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi = [None] * period  # Padding initial values
        
        # Initial RS value
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

        # Smoothly calculate RSI using the Wilder’s formula
        for i in range(period + 1, len(data)):
            avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))

        # Discard the first n candlesticks if specified
        rsi = rsi[period:]
            
        return rsi
