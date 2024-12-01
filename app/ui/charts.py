from PyQt5.QtWidgets import QVBoxLayout, QWidget, QGraphicsRectItem
import pyqtgraph as pg
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

    def update_chart(self, candlestick_data):
        """Updates the chart with standard candlestick format and adjusts scale."""
        self.chart.clear()

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



class VolumeChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Volume Chart", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.chart.setLabel('bottom', 'Time')
        self.chart.setLabel('left', 'Volume')
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, candlestick_data):
        """Updates the volume chart with bars using distinct colors for buy/sell and adjusts scale."""
        self.chart.clear()

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

    def update_chart(self, depth_data):
        """Updates the depth chart with cumulative data and adjusts scale."""
        self.chart.clear()

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

