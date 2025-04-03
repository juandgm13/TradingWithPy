from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QLineEdit, QTabWidget, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QIcon
from app.api.api_manager import APIManager
from app.utils.config import ConfigLoader
from app.ui.tabs_definition import TradingViewTab, OrdersTab, BalanceTab
from app.utils.logger import setup_logger

class DataUpdateWorker(QThread):
    update_tab = pyqtSignal(object, object, object, object, object)

    error_occurred = pyqtSignal(str)

    def __init__(self, api_manager, trading_pair, interval='1h', selected_tab="TradingView"):
        super().__init__()
        self.api_manager = api_manager
        self.trading_pair = trading_pair
        self.interval = interval
        self.selected_tab=selected_tab

        # Initialize the config loader
        config = ConfigLoader("app/utils/config/config.json")

        # Retrieve values from the configuration
        self.num_candles = config.get("num_candles", 100)
        self.rsi_period = config.get("indicators_period", 14)
    
    def emit_update_tab(self, candlesticks_data=None, depth_data=None, rsi_period_data=None, orders_data=None, balance_data=None):
        # Emit the signal, providing default None values where necessary
        self.update_tab.emit(candlesticks_data, depth_data, rsi_period_data, orders_data, balance_data)

    def run(self):
        try:
            if self.selected_tab=="TradingView" or self.selected_tab=="Orders":
                depth = self.api_manager.get_depth_data(self.trading_pair, limit=(self.num_candles+self.rsi_period))
                
                if self.selected_tab=="TradingView":
                    # Fetch candlestick and depth data
                    candlesticks = self.api_manager.get_candlestick_data(self.trading_pair, interval=self.interval, limit=(self.num_candles+self.rsi_period))
                    # Emit the data
                    self.emit_update_tab(candlesticks_data=candlesticks, depth_data=depth, rsi_period_data=self.rsi_period)
                if self.selected_tab=="Orders":
                    orders = self.api_manager.get_open_orders(self.trading_pair)
                    # Emit the data
                    self.emit_update_tab(orders_data=orders, depth_data=depth)
            if self.selected_tab=="Balance":
                balance = self.api_manager.get_account_balances()
                # Emit the data
                self.emit_update_tab(balance_data=balance)
            
        except Exception as e:
            # Emit the error
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, logger=None):
        super().__init__()

        # Initialize the config loader
        config = ConfigLoader("app/utils/config/config.json")

        # Retrieve values from the configuration
        self.num_candles = config.get("num_candles", 100)
        self.rsi_period = config.get("indicators_period", 14)
        self.timer_interval = config.get("timer_interval_ms", 5000)

        # Set the window icon
        self.setWindowIcon(QIcon('app/resources/AppIcon.ico'))

        self.setWindowTitle("Trading Dashboard")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize logger
        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger

        # Initialize API manager
        self.api_manager = APIManager(logger=self.logger)

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
        self.update_timer.timeout.connect(self.start_main_window_update)
        self.update_timer.start(self.timer_interval)

        # Select the first item in the list of api clients
        self.select_api(self.api_manager.get_api_clients_list()[0])

    def select_api(self, api_name):
        self.reset_update_timer()

        self.api_manager.set_api(api_name)

        self.trading_pairs = self.api_manager.get_trading_symbols()
        self.filtered_pairs = self.trading_pairs[:]  # Copy for filtering 

        # Update dropdown for selecting trading pair
        self.pair_selector.clear()
        self.pair_selector.addItems(self.trading_pairs)
        if "BTCUSDC" in self.trading_pairs:
            self.current_pair = "BTCUSDC" 
        elif "BTC/USDC" in self.trading_pairs:
            self.current_pair = "BTC/USDC" 
        else:
            self.trading_pairs[0]
        self.pair_selector.setCurrentText(self.current_pair)

        # Default pair for binance

        self.start_main_window_update()

    def reset_update_timer(self):
        """Stop and restart the update timer"""
        self.update_timer.stop()  
        self.update_timer.start(self.timer_interval)
        self.logger.info("Update timer has been reset.")
        
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

    def init_ui(self):
        layout = QVBoxLayout()  # Use QVBoxLayout to stack widgets vertically

        # Create the top layout for trading pair selection and info
        top_layout = QVBoxLayout()

        # Dropdown for selecting API
        self.api_selector = QComboBox()
        self.api_selector.addItems(self.api_manager.get_api_clients_list())
        self.api_selector.setCurrentText(self.api_manager.get_api_clients_list()[0])
        self.api_selector.setStyleSheet("color: white; background-color: #2e2e2e;")
        self.api_selector.currentTextChanged.connect(self.on_api_changed)
        top_layout.addWidget(QLabel("Select API:"))
        top_layout.addWidget(self.api_selector)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search trading pairs...")
        self.search_input.setStyleSheet("color: white; background-color: #2e2e2e;")
        self.search_input.textChanged.connect(self.filter_pairs)
        top_layout.addWidget(self.search_input)

        # Dropdown for selecting trading pair
        self.pair_selector = QComboBox()
        #self.pair_selector.addItems(self.trading_pairs)
        #self.pair_selector.setCurrentText(self.current_pair)
        self.pair_selector.setStyleSheet("color: white; background-color: #2e2e2e;")
        self.pair_selector.currentTextChanged.connect(self.on_pair_changed)
        top_layout.addWidget(QLabel("Select Trading Pair:"))
        top_layout.addWidget(self.pair_selector)

        # Info Panel (Displaying trading pair details)
        self.info_panel = QVBoxLayout()
        self.info_panel_1 = QHBoxLayout()
        self.info_panel_2 = QHBoxLayout()

        self.name_label = QLabel("Name: -")
        self.name_label.setStyleSheet("color: white;")
        self.exchange_label = QLabel("Exchange: -")
        self.exchange_label.setStyleSheet("color: white;")

        self.info_panel_1.addWidget(self.name_label)
        self.info_panel_1.addWidget(self.exchange_label)

        self.price_label = QLabel("Price: -")
        self.price_label.setStyleSheet("color: white;")
        self.high_low_label = QLabel("24h High/Low: -")
        self.high_low_label.setStyleSheet("color: white;")
        self.volume_label = QLabel("24h Volume: -")
        self.volume_label.setStyleSheet("color: white;")

        self.info_panel_2.addWidget(self.price_label)
        self.info_panel_2.addWidget(self.high_low_label)
        self.info_panel_2.addWidget(self.volume_label)

        self.info_panel.addLayout(self.info_panel_1)
        self.info_panel.addLayout(self.info_panel_2)
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

        self.trading_view_tab = TradingViewTab(logger=self.logger)
        self.tab_widget.addTab(self.trading_view_tab, "Trading View")

        # Connect signal of trading view tab
        self.trading_view_tab.interval_changed.connect(self.update_interval)
        self.trading_view_tab.need_update.connect(self.start_main_window_update)

        self.orders_tab = OrdersTab(logger=self.logger)
        self.tab_widget.addTab(self.orders_tab, "Orders")

        # Connect the OrdersTab signal to the main window's order creation handler
        self.orders_tab.order_requested.connect(self.handle_order_request)

        self.balance_Tab = BalanceTab(logger=self.logger)
        self.tab_widget.addTab(self.balance_Tab, "Balance")

        # Connect the tab change signal to a handler
        self.tab_widget.currentChanged.connect(self.handle_tab_change)


        self.handle_tab_change(self.tab_widget.currentIndex(), False)
        
        # Add the tab widget below the trading pair information
        layout.addWidget(self.tab_widget)

        # Set the layout for the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_tab_change(self, index, update=True):
        """
        Handles tab change events and updates only the visible tab.
        """
        current_tab = self.tab_widget.widget(index)
        if current_tab == self.trading_view_tab:
            self.tab_selected="TradingView"
        elif current_tab == self.orders_tab:
            self.tab_selected="Orders"
        elif current_tab == self.balance_Tab:
            self.tab_selected="Balance"
        
        if(update):
            self.start_main_window_update()

    def handle_order_request(self, order_details):
        """
        Handles the order request signal from the OrdersTab and places the order using the API.
        """
        order_details["symbol"] = self.current_pair  # Add the selected pair from the main window context
        order_details["type"] = "LIMIT"  # Assuming LIMIT order by default

        try:
            response = self.api_manager.place_order(order_details)
            self.logger.info(f"Order placed: {response}")
            # Format the order details for the message
            message = (
                f"Side: {response.get('side', 'Unknown')}\n"
                f"Symbol: {response.get('symbol', 'Unknown')}\n"
                f"Price: {response.get('price', 'Unknown')}\n"
                f"Quantity: {response.get('origQty', 'Unknown')}\n"
                f"Order ID: {response.get('orderId', 'Unknown')}\n"
                f"Status: {response.get('status', 'Unknown')}"
            )
            self.show_popup("Order Created Successfully!", message)
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            self.show_popup("Order Creation Failed!", e.error_message)

    def update_interval(self, new_interval):
        self.logger.info(f"Interval has been updated ({self.selected_interval}->{new_interval}).")
        self.selected_interval = new_interval
        self.start_main_window_update()

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

    def on_api_changed(self, api_name):
        """Handles change in api selection."""
        self.select_api(api_name)

    def on_pair_changed(self, trading_pair):
        """Handles change in trading pair selection."""
        self.current_pair = trading_pair
        self.start_main_window_update()

    def update_pair_info(self):
        """Fetches and updates the trading pair information."""
        try:
            SelectedSymbol=self.api_manager.get_symbol_info(self.current_pair)
            self.name_label.setText(f"Name: {SelectedSymbol.name}")
            self.exchange_label.setText(f"Exchange: {SelectedSymbol.exchange}")
            
            info = self.api_manager.get_ticker_info(self.current_pair)
            # Assume `info` contains: {'price': float, 'high': float, 'low': float, 'volume': float}
            self.price_label.setText(f"Price: {info['price']:.2f}")
            self.high_low_label.setText(f"24h High/Low: {info['high']:.2f} / {info['low']:.2f}")
            self.volume_label.setText(f"24h Volume: {info['volume']:.2f}")
            self.logger.info(f"Updated pair info for {self.current_pair}.")
        except Exception as e:
            self.logger.error(f"Failed to update pair info: {e}")
            self.show_error_message(f"Failed to fetch info for {self.current_pair}")

    def start_main_window_update(self):
        """Starts the main window update process in a background thread."""
        self.reset_update_timer()
        if not self.current_pair:
            self.logger.warning("No trading pair selected to update main window.")
            return

        if self.chart_worker and self.chart_worker.isRunning():
            self.logger.warning("main window update is already in progress. Skipping this update.")
            return

        self.logger.info(f"Starting main window update for {self.current_pair} with interval {self.selected_interval}.")
        self.chart_worker = DataUpdateWorker(self.api_manager, self.current_pair, self.selected_interval, self.tab_selected)
        self.chart_worker.update_tab.connect(self.update_main_window)
        self.chart_worker.error_occurred.connect(self.handle_update_main_window_error)
        self.chart_worker.start()

    def update_main_window(self, candlesticks=None, depth=None, rsi_period=None, orders=None, balance=None):
        self.logger.info(f"Window update showing {self.tab_selected} information.")
        if (self.tab_selected=="TradingView"):
            self.trading_view_tab.update(candlesticks, depth, rsi_period)
        if (self.tab_selected=="Orders"):
            self.orders_tab.update(open_orders=orders, order_book_data=depth)
        if (self.tab_selected=="Balance"):
            self.balance_Tab.update(balances=balance)
        
        self.update_pair_info()

    def handle_update_main_window_error(self, error_message):
        """Handles errors that occur during main window update."""
        self.logger.error(f"Chart update error: {error_message}")
        self.show_error_message(error_message)

    def show_error_message(self, message):
        """Placeholder for actual error message handling in UI."""
        self.logger.warning(f"Error: {message}")

    def show_popup(self, title, message):
        """
        Displays a popup with a message.

        Args:
            title: title for the message box.
            message: text to show.
        """
        # Create a message box
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # Add an OK button to close the popup
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Show the message box
        msg_box.exec_()

