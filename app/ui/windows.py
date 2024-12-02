from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QLineEdit, QTabWidget, QHBoxLayout, QRadioButton, QCheckBox
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QIcon
from app.utils.logger import setup_logger, verbose_level
from app.api.api_wrapper import APIWrapper
from app.ui.charts import CandlestickChart, VolumeChart, DepthChart, RSIChart
from app.utils.config import ConfigLoader

class ChartUpdateWorker(QThread):
    data_fetched = pyqtSignal(list, dict)  # Emit a list for candlesticks and a dict for depth
    error_occurred = pyqtSignal(str)

    def __init__(self, api_wrapper, trading_pair, interval='1h'):
        super().__init__()
        self.api_wrapper = api_wrapper
        self.trading_pair = trading_pair
        self.interval = interval

        # Initialize the config loader
        config = ConfigLoader("app/utils/config/config.json")

        # Retrieve values from the configuration
        self.num_candles = config.get("num_candles", 100)
        self.rsi_period = config.get("rsi_period", 14)
    
    def run(self):
        try:
            # Fetch candlestick and depth data
            candlesticks = self.api_wrapper.get_candlestick_data(self.trading_pair, interval=self.interval, limit=(self.num_candles+self.rsi_period))
            depth = self.api_wrapper.get_depth_data(self.trading_pair, limit=(self.num_candles+self.rsi_period))

            # Emit the data
            self.data_fetched.emit(candlesticks, depth)
        except Exception as e:
            # Emit the error
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the config loader
        config = ConfigLoader("app/utils/config/config.json")

        # Retrieve values from the configuration
        self.num_candles = config.get("num_candles", 100)
        self.rsi_period = config.get("rsi_period", 14)

        # Set the window icon
        self.setWindowIcon(QIcon('app/resources/AppIcon.ico'))

        self.setWindowTitle("Trading Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize logger and API wrapper
        self.logger = setup_logger()  # Use the updated logger setup
        self.logger.setLevel(verbose_level)
        self.api_wrapper = APIWrapper(api_name="binance")  # Initialize with Binance API

        self.trading_pairs = self.api_wrapper.get_trading_pairs()
        self.filtered_pairs = self.trading_pairs[:]  # Copy for filtering

        # Default pair
        self.current_pair = "BTCUSDT" if "BTCUSDT" in self.trading_pairs else self.trading_pairs[0]

        # Initialize the chart worker
        self.chart_worker = None

        # Default candlestick interval
        self.selected_interval = '1h'

        # Create UI
        self.init_ui()

        # Apply dark mode to the window
        self.apply_dark_mode()

        # Start a timer to update charts every 5 seconds
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.start_chart_update)
        self.update_timer.timeout.connect(self.update_pair_info)
        self.update_timer.start(5000)

    def apply_dark_mode(self):
        """Apply dark mode to the entire application and customize radio buttons and checkboxes."""
        palette = QPalette()

        # Set dark background
        palette.setColor(QPalette.Window, QColor(53, 53, 53))  # Dark background color
        palette.setColor(QPalette.WindowText, Qt.white)  # White text

        # Set darker colors for other elements
        palette.setColor(QPalette.Base, QColor(42, 42, 42))  # Background color of text inputs
        palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))  # Alternate background color
        palette.setColor(QPalette.ToolTipBase, Qt.white)  # Tooltip text color
        palette.setColor(QPalette.ToolTipText, Qt.white)  # Tooltip background color

        # Set the highlight color (for selected text, etc.)
        palette.setColor(QPalette.Highlight, QColor(46, 132, 255))  # Highlight color (blue)
        palette.setColor(QPalette.HighlightedText, Qt.white)  # Selected text color

        # Apply the palette to the entire application
        self.setPalette(palette)

        # Define a common stylesheet for radio buttons
        self.radio_button_style = """
            QRadioButton {
                color: white;
                background-color: transparent;
            }
            QRadioButton::indicator {
                border: 1px solid #444444;
                background-color: #2e2e2e;
            }
            QRadioButton::indicator:checked {
                background-color: #444444;
            }
        """

        # Define a common stylesheet for checkboxes
        self.checkbox_style = """
            QCheckBox {
                color: white;
                background-color: transparent;
            }
            QCheckBox::indicator {
                border: 1px solid #444444;
                background-color: #2e2e2e;
            }
            QCheckBox::indicator:checked {
                background-color: #444444;
            }
        """
        
        # List of all radio buttons
        radio_buttons = [self.radio_15m, self.radio_1h, self.radio_4h, self.radio_1d]

        # Apply the style to each radio button
        for radio_button in radio_buttons:
            radio_button.setStyleSheet(self.radio_button_style)

        # List of all checkboxes (replace with your actual checkboxes)
        checkboxes = [self.sma_checkbox, self.ema_checkbox, self.rsi_checkbox, self.bollinger_checkbox]  

        # Apply the style to each checkbox
        for checkbox in checkboxes:
            checkbox.setStyleSheet(self.checkbox_style)

    def update_checkbox_color(self):
        if self.ema_checkbox.isChecked():
            checkbox_style = """
                                QCheckBox {
                                    color: orange;  /* Text color */
                                    background-color: transparent;
                                }
                            """
            self.ema_checkbox.setStyleSheet(checkbox_style)
        else:
            self.ema_checkbox.setStyleSheet(self.checkbox_style)
        
        if self.sma_checkbox.isChecked():
            checkbox_style = """
                                QCheckBox {
                                    color: blue;  /* Text color */
                                    background-color: transparent;
                                }
                            """
            self.sma_checkbox.setStyleSheet(checkbox_style)
        else:
            self.sma_checkbox.setStyleSheet(self.checkbox_style)
        

    def init_ui(self):
        layout = QVBoxLayout()  # Use QVBoxLayout to stack widgets vertically

        # Create the top layout for trading pair selection and info
        top_layout = QVBoxLayout()

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search trading pairs...")
        self.search_input.setStyleSheet("color: white; background-color: #2e2e2e;")
        self.search_input.textChanged.connect(self.filter_pairs)
        top_layout.addWidget(self.search_input)

        # Dropdown for selecting trading pair
        self.pair_selector = QComboBox()
        self.pair_selector.addItems(self.trading_pairs)
        self.pair_selector.setCurrentText(self.current_pair)
        self.pair_selector.setStyleSheet("color: white; background-color: #2e2e2e;")
        self.pair_selector.currentTextChanged.connect(self.on_pair_changed)
        top_layout.addWidget(QLabel("Select Trading Pair:"))
        top_layout.addWidget(self.pair_selector)

        # Info Panel (Displaying trading pair details)
        self.info_panel = QHBoxLayout()

        self.price_label = QLabel("Price: -")
        self.price_label.setStyleSheet("color: white;")
        self.change_label = QLabel("24h Change: -")
        self.change_label.setStyleSheet("color: white;")
        self.high_low_label = QLabel("24h High/Low: -")
        self.high_low_label.setStyleSheet("color: white;")
        self.volume_label = QLabel("24h Volume: -")
        self.volume_label.setStyleSheet("color: white;")

        self.info_panel.addWidget(self.price_label)
        self.info_panel.addWidget(self.change_label)
        self.info_panel.addWidget(self.high_low_label)
        self.info_panel.addWidget(self.volume_label)

        top_layout.addLayout(self.info_panel)

        # Add the top layout to the main layout (above the tab view)
        layout.addLayout(top_layout)

        # Tab widget for charts
        self.tab_widget = QTabWidget()

        # Set the tab's background and borders for dark mode
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #2e2e2e;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabWidget::tab {
                background-color: #2e2e2e;
                color: white;
                padding: 5px;
                margin-right: 5px;
                border: 1px solid #444444;
            }
            QTabWidget::tab:selected {
                background-color: #444444;
            }
        """)

        # Initialize chart widgets
        self.charts_container = QWidget()
        horizontal_layout = QHBoxLayout()

        # Left side: Candlestick, Volume, Depth charts
        charts_left_layout = QVBoxLayout()

        # Add a new layout for indicator selection
        self.indicator_layout = QVBoxLayout()
        self.indicators_label = QLabel("Indicators:")
        self.indicators_label.setStyleSheet("color: white;")
        self.indicator_layout.addWidget(self.indicators_label)

        # Checkboxes for indicators
        self.sma_checkbox = QCheckBox("SMA (Simple Moving Average)")
        self.ema_checkbox = QCheckBox("EMA (Exponential Moving Average)")
        self.rsi_checkbox = QCheckBox("RSI (Relative Strength Index)")
        self.bollinger_checkbox = QCheckBox("Bollinger Bands")

        # Add checkboxes to layout
        self.indicator_layout.addWidget(self.sma_checkbox)
        self.indicator_layout.addWidget(self.ema_checkbox)
        self.indicator_layout.addWidget(self.rsi_checkbox)
        self.indicator_layout.addWidget(self.bollinger_checkbox)


        self.candlestick_chart = CandlestickChart()
        self.volume_chart = VolumeChart()
        self.depth_chart = DepthChart()

        # Initialize RSI chart widget (Initially hidden)
        self.rsi_chart = RSIChart()
        self.rsi_chart.setVisible(False)  

        # First section: Radio buttons for different intervals
        self.radio_buttons_layout = QHBoxLayout()

        # Create radio buttons for different intervals
        self.radio_15m = QRadioButton("15 Min")
        self.radio_1h = QRadioButton("1 Hour")
        self.radio_4h = QRadioButton("4 Hour")
        self.radio_1d = QRadioButton("1 Day")
        self.radio_15m.setMaximumWidth(55)
        self.radio_1h.setMaximumWidth(35)
        self.radio_4h.setMaximumWidth(35)
        self.radio_1d.setMaximumWidth(35)

        # Set default selection for 1 Hour
        self.radio_1h.setChecked(True)

        # Add radio buttons to layout
        self.radio_buttons_layout.addWidget(self.radio_15m)
        self.radio_buttons_layout.addWidget(self.radio_1h)
        self.radio_buttons_layout.addWidget(self.radio_4h)
        self.radio_buttons_layout.addWidget(self.radio_1d)
        self.radio_buttons_layout.addStretch()

        # Connect radio buttons to the function that handles the selection
        self.radio_15m.toggled.connect(self.update_interval)
        self.radio_1h.toggled.connect(self.update_interval)
        self.radio_4h.toggled.connect(self.update_interval)
        self.radio_1d.toggled.connect(self.update_interval)

        # Add candlestick chart

        # Add charts to the left layout
        charts_left_layout.addLayout(self.radio_buttons_layout)
        charts_left_layout.addWidget(self.candlestick_chart)
        charts_left_layout.addWidget(self.volume_chart)
        charts_left_layout.addWidget(self.depth_chart)
        charts_left_layout.addWidget(self.rsi_chart)

        horizontal_layout.addLayout(charts_left_layout)

        # Right side: Radio buttons for selecting interval
        right_vertical_layout = QVBoxLayout()


        # Add indicator layout to the right panel
        right_vertical_layout.addLayout(self.indicator_layout)
        right_vertical_layout.addStretch()

        # Add an empty panel below the radio buttons for debug purposes
        #empty_panel_1 = QWidget()
        #empty_layout_1 = QVBoxLayout()
        #empty_layout_1.addWidget(QLabel("Empty Panel 1"))
        #empty_panel_1.setLayout(empty_layout_1)
        #empty_panel_1.setStyleSheet("background-color: #444444; color: white;")
        #right_vertical_layout.addWidget(empty_panel_1)

        # Second section: Empty panel with debug text
        #empty_panel_2 = QWidget()
        #empty_layout_2 = QVBoxLayout()
        ##empty_layout_2.addWidget(QLabel("Empty Panel 2"))
        #empty_panel_2.setLayout(empty_layout_2)
        #empty_panel_2.setStyleSheet("background-color: #444444; color: white;")
        #right_vertical_layout.addWidget(empty_panel_2)

        # Add the right side layout (which contains radio buttons and empty panels) to the tab
        horizontal_layout.addLayout(right_vertical_layout)

        self.charts_container.setLayout(horizontal_layout)
        self.tab_widget.addTab(self.charts_container, "Trading View")

        # Add the tab widget below the trading pair information
        layout.addWidget(self.tab_widget)

        # Set the layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


        # Load initial data
        self.start_chart_update()
        self.update_pair_info()

        # Connect checkboxes to their respective functions
        self.sma_checkbox.stateChanged.connect(self.update_interval)
        self.ema_checkbox.stateChanged.connect(self.update_interval)
        self.rsi_checkbox.stateChanged.connect(self.toggle_rsi)
        self.bollinger_checkbox.stateChanged.connect(self.update_interval)

    def filter_pairs(self, search_text):
        """Filters the trading pairs in the dropdown based on search input."""
        search_text = search_text.upper()  # Ensure case-insensitivity
        self.filtered_pairs = [pair for pair in self.trading_pairs if search_text in pair]

        # Update the dropdown
        self.pair_selector.clear()
        self.pair_selector.addItems(self.filtered_pairs)

        # Reset to the first filtered pair or clear if none match
        if self.filtered_pairs:
            self.pair_selector.setCurrentIndex(0)
            self.on_pair_changed(self.pair_selector.currentText())
        else:
            self.on_pair_changed("")  # Clear the charts if no match

    def on_pair_changed(self, trading_pair):
        """Handles change in trading pair selection."""
        self.current_pair = trading_pair
        self.start_chart_update()
        self.update_pair_info()

    def update_interval(self):
        """Updates the candlestick chart interval based on selected radio button."""
        if self.radio_15m.isChecked():
            self.selected_interval = '15m'
        elif self.radio_1h.isChecked():
            self.selected_interval = '1h'
        elif self.radio_4h.isChecked():
            self.selected_interval = '4h'
        elif self.radio_1d.isChecked():
            self.selected_interval = '1d'

        self.update_checkbox_color()
        self.start_chart_update()

    def start_chart_update(self):
        """Starts the chart update process in a background thread."""
        if not self.current_pair:
            self.logger.warning("No trading pair selected to update charts.")
            return

        if self.chart_worker and self.chart_worker.isRunning():
            self.logger.warning("Chart update is already in progress. Skipping this update.")
            return

        self.logger.debug(f"Starting chart update for {self.current_pair} with interval {self.selected_interval}.")
        self.chart_worker = ChartUpdateWorker(self.api_wrapper, self.current_pair, self.selected_interval)
        self.chart_worker.data_fetched.connect(self.update_charts)
        self.chart_worker.error_occurred.connect(self.handle_chart_update_error)
        self.chart_worker.start()

    def update_charts(self, candlesticks, depth):
        """Updates the charts with fetched data, including RSI."""
        try:
            # Update candlestick chart
            try:
                self.candlestick_chart.update_chart(candlesticks, self.rsi_period, 
                                                    self.sma_checkbox.isChecked(),
                                                    self.ema_checkbox.isChecked(),
                                                    self.bollinger_checkbox.isChecked())                    
                self.logger.info("Candlestick chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update candlestick chart: {e}")
                self.show_error_message(f"Candlestick chart error: {e}")
            
            # Update volume chart
            try:
                self.volume_chart.update_chart(candlesticks, self.rsi_period)
                self.logger.info("Volume chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update volume chart: {e}")
                self.show_error_message(f"Volume chart error: {e}")

            # Update depth chart
            try:
                self.depth_chart.update_chart(depth, self.rsi_period)
                self.logger.info("Depth chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update depth chart: {e}")
                self.show_error_message(f"Depth chart error: {e}")
            
            # Update RSI chart if there is enough data
            try:
                if len(candlesticks) > self.rsi_period:  # Ensure there's enough data for the default RSI period (14)
                    closing_prices = [float(c[4]) for c in candlesticks]  # Extract closing prices
                    self.rsi_chart.update_chart(closing_prices, period=self.rsi_period)
                    self.logger.info("RSI chart updated successfully.")
                else:
                    self.logger.warning("Not enough candlestick data to update RSI chart.")
            except Exception as e:
                self.logger.error(f"Failed to update RSI chart: {e}")
                self.show_error_message(f"RSI chart error: {e}")
            
            self.logger.info(f"Charts updated for {self.current_pair}.")

        except Exception as e:
            self.logger.critical(f"Critical error during chart update: {e}")
            self.show_error_message(f"Critical error: {str(e)}")

    def toggle_rsi(self):
        self.rsi_chart.setVisible(self.rsi_checkbox.isChecked())
          

    def handle_chart_update_error(self, error_message):
        """Handles errors that occur during chart updates."""
        self.logger.error(f"Chart update error: {error_message}")
        self.show_error_message(error_message)

    def show_error_message(self, message):
        """Placeholder for actual error message handling in UI."""
        self.logger.warning(f"Error: {message}")

    def update_pair_info(self):
        """Fetches and updates the trading pair information."""
        try:
            info = self.api_wrapper.get_ticker_info(self.current_pair)
            # Assume `info` contains: {'price': float, 'change': float, 'high': float, 'low': float, 'volume': float}
            self.price_label.setText(f"Price: {info['price']:.2f}")
            self.change_label.setText(f"24h Change: {info['change']:.2f}%")
            self.high_low_label.setText(f"24h High/Low: {info['high']:.2f} / {info['low']:.2f}")
            self.volume_label.setText(f"24h Volume: {info['volume']:.2f}")
            self.logger.info(f"Updated pair info for {self.current_pair}.")
        except Exception as e:
            self.logger.error(f"Failed to update pair info: {e}")
            self.show_error_message(f"Failed to fetch info for {self.current_pair}")

