from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg


class CandlestickChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Candlestick Chart")
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, candlestick_data):
        self.chart.clear()
        times = [c[0] for c in candlestick_data]
        highs = [float(c[2]) for c in candlestick_data]
        lows = [float(c[3]) for c in candlestick_data]
        opens = [float(c[1]) for c in candlestick_data]
        closes = [float(c[4]) for c in candlestick_data]
        for i, (t, o, h, l, c) in enumerate(zip(times, opens, highs, lows, closes)):
            color = 'g' if c >= o else 'r'
            self.chart.plot([t, t], [l, h], pen=color)
            self.chart.plot([t, t], [o, c], pen=color, symbol='o')


class VolumeChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Volume Chart")
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, candlestick_data):
        self.chart.clear()
        times = [c[0] for c in candlestick_data]
        volumes = [float(c[5]) for c in candlestick_data]
        self.chart.plot(times, volumes, pen='b')


class DepthChart(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.chart = pg.PlotWidget(title="Depth Chart")
        layout.addWidget(self.chart)
        self.setLayout(layout)

    def update_chart(self, depth_data):
        self.chart.clear()
        bids = depth_data['bids']
        asks = depth_data['asks']
        bid_prices = [float(b[0]) for b in bids]
        bid_volumes = [float(b[1]) for b in bids]
        ask_prices = [float(a[0]) for a in asks]
        ask_volumes = [float(a[1]) for a in asks]
        self.chart.plot(bid_prices, bid_volumes, pen='g', fillLevel=0, brush=(50, 200, 50, 50))
        self.chart.plot(ask_prices, ask_volumes, pen='r', fillLevel=0, brush=(200, 50, 50, 50))
