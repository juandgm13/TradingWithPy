import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QLabel
from app.api.api_wrapper import APIWrapper
from app.ui.charts import  CandlestickChart, VolumeChart, DepthChart
from app.utils.logger import setup_logger, verbose_level


def create_main_window():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize logger and API wrapper
        self.logger = setup_logger()  # Use the updated logger setup
        self.logger.setLevel(verbose_level)
        self.api_wrapper = APIWrapper(api_name="binance")  # Initialize with Binance API

        self.trading_pairs = self.api_wrapper.get_trading_pairs()

        # Create UI
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown for selecting trading pair
        self.pair_selector = QComboBox()
        self.pair_selector.addItems(self.trading_pairs)
        self.pair_selector.currentTextChanged.connect(self.update_charts)
        layout.addWidget(QLabel("Select Trading Pair:"))
        layout.addWidget(self.pair_selector)

        # Charts
        self.candlestick_chart = CandlestickChart()
        self.volume_chart = VolumeChart()
        self.depth_chart = DepthChart()

        layout.addWidget(self.candlestick_chart)
        layout.addWidget(self.volume_chart)
        layout.addWidget(self.depth_chart)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Load initial data
        self.update_charts(self.pair_selector.currentText())

    def update_charts(self, trading_pair):
        # Log the update event
        self.logger.debug(f"Updating charts for {trading_pair}")

        try:
            # Fetch data using API wrapper
            candlesticks = self.api_wrapper.get_candlestick_data(trading_pair)
            depth = self.api_wrapper.get_depth_data(trading_pair)

            # Update charts
            self.candlestick_chart.update_chart(candlesticks)
            self.volume_chart.update_chart(candlesticks)
            self.depth_chart.update_chart(depth)
        
        except Exception as e:
            self.logger.error(f"Failed to update charts: {e}")
            self.show_error_message(str(e))
    
    def show_error_message(self, message):
        # This is a placeholder for an actual UI error message
        self.logger.warning(f"Error: {message}")
