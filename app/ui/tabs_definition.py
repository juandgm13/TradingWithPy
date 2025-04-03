from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QPushButton, QLineEdit, QTabWidget, QFormLayout, QSplitter,
    QCheckBox, QRadioButton, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QColor
from app.ui.charts import CandlestickChart, VolumeChart, DepthChart, RSIChart
from PyQt5.QtCore import pyqtSignal,Qt
from app.utils.logger import setup_logger

class TradingViewTab(QWidget):
    need_update = pyqtSignal()  # Signal to call update in main window
    interval_changed = pyqtSignal(str)  # Signal to notify about updates

    def __init__(self, logger=None):
        super().__init__()
        
        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger
        
        # Initialize ui
        self.init_ui()

        # Apply Dark mode 
        self.apply_dark_mode_to_tab()

    def init_ui(self):
        """
        Initialize the UI components for the tab.
        """

        self.main_H_layout = QHBoxLayout()

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

        # Charts definition
        self.candlestick_chart = CandlestickChart()
        self.volume_chart = VolumeChart()
        self.depth_chart = DepthChart()

        # Initialize RSI chart widget (Initially hidden)
        self.rsi_chart = RSIChart()
        self.rsi_chart.setVisible(False)  
        
        # Radio buttons for different intervals
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
        self.selected_interval='1h'

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

        # Add to main layout
        self.main_H_layout.addLayout(charts_left_layout)

        # Right side: Radio buttons for selecting interval
        right_vertical_layout = QVBoxLayout()

        # Add indicator layout to the right panel
        right_vertical_layout.addLayout(self.indicator_layout)
        right_vertical_layout.addStretch()

        # Add the right side layout (which contains indicators) to the tab
        self.main_H_layout.addLayout(right_vertical_layout)

        self.setLayout(self.main_H_layout)

        # Connect checkboxes to their respective functions
        self.sma_checkbox.stateChanged.connect(self.update_checkbox)
        self.ema_checkbox.stateChanged.connect(self.update_checkbox)
        self.bollinger_checkbox.stateChanged.connect(self.update_checkbox)
        self.rsi_checkbox.stateChanged.connect(self.toggle_rsi)

    def apply_dark_mode_to_tab(self):
        """
        Apply dark mode to the entire application and customize radio buttons and checkboxes.
        """
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

    def update(self, candlesticks, depth, rsi_period):
        """
        Update the tab's content using the provided data.
        """
        try:
            # Update candlestick chart
            try:
                self.candlestick_chart.update_chart(candlesticks, rsi_period, 
                                                    self.sma_checkbox.isChecked(),
                                                    self.ema_checkbox.isChecked(),
                                                    self.bollinger_checkbox.isChecked())                    
                self.logger.info("Candlestick chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update candlestick chart: {e}")
                self.show_error_message(f"Candlestick chart error: {e}")
            
            # Update volume chart
            try:
                self.volume_chart.update_chart(candlesticks, rsi_period)
                self.logger.info("Volume chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update volume chart: {e}")
                self.show_error_message(f"Volume chart error: {e}")

            # Update depth chart
            try:
                if(depth==None):
                    self.depth_chart.setVisible(False)
                else:
                    self.depth_chart.setVisible(True)
                    self.depth_chart.update_chart(depth, rsi_period)
                    self.logger.info("Depth chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update depth chart: {e}")
                self.show_error_message(f"Depth chart error: {e}")
            
            # Update RSI chart if there is enough data
            try:
                if len(candlesticks) > rsi_period:  # Ensure there's enough data for the default RSI period (14)
                    self.rsi_chart.update_chart(candlesticks, period=rsi_period)
                    self.logger.info("RSI chart updated successfully.")
                else:
                    self.logger.warning("Not enough candlestick data to update RSI chart.")
            except Exception as e:
                self.logger.error(f"Failed to update RSI chart: {e}")
                self.show_error_message(f"RSI chart error: {e}")
            
            self.logger.info(f"Charts updated.")

        except Exception as e:
            self.logger.critical(f"Critical error during chart update: {e}")
            self.show_error_message(f"Critical error: {str(e)}")
    
    def update_interval(self):
        """Updates the candlestick chart interval based on selected radio button."""
        if self.radio_15m.isChecked():
            new_selected_interval = '15m'
        elif self.radio_1h.isChecked():
            new_selected_interval = '1h'
        elif self.radio_4h.isChecked():
            new_selected_interval = '4h'
        elif self.radio_1d.isChecked():
            new_selected_interval = '1d'

        if new_selected_interval != self.selected_interval:
            self.selected_interval=new_selected_interval
            self.interval_changed.emit(self.selected_interval)

    def call_update_main_window(self):
        """call to start_main_window_update"""
        self.logger.info(f"Call to start_main_window_update from TradingViewTab.")
        self.need_update.emit()

    def update_checkbox(self):
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

        self.call_update_main_window()

    def toggle_rsi(self):
        self.rsi_chart.setVisible(self.rsi_checkbox.isChecked())

    def show_error_message(self, message):
        """Placeholder for actual error message handling in UI."""
        self.logger.warning(f"Error: {message}")



class OrdersTab(QWidget):
    order_requested = pyqtSignal(dict)  # Signal to send order details to the main window

    def __init__(self, logger=None):
        super().__init__()

        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger
        
        # Initialize ui
        self.init_ui()
        
        # Apply Dark mode 
        self.apply_dark_mode_to_tab()
        
    def init_ui(self):
        """
        Initialize the UI components for the tab.
        """
        # Layouts
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Tab container for Buy/Sell
        self.buy_sell_tabs = QTabWidget()
        self.buy_sell_tabs.setTabPosition(QTabWidget.North)

        # Create separate layouts for Buy and Sell tabs
        buy_tab = QWidget()
        sell_tab = QWidget()

        # Layout for the Buy tab
        buy_tab_layout = QVBoxLayout()
        buy_form_layout = QFormLayout()

        # Buy Price input
        self.buy_price_input = QLineEdit()
        self.buy_price_input.setPlaceholderText("Enter price")
        buy_form_layout.addRow("Price:", self.buy_price_input)

        # Buy Quantity input
        self.buy_quantity_input = QLineEdit()
        self.buy_quantity_input.setPlaceholderText("Enter quantity")
        buy_form_layout.addRow("Quantity:", self.buy_quantity_input)

        # Execute Buy order button
        self.buy_place_order_button = QPushButton("Place Buy Order")
        self.buy_place_order_button.clicked.connect(self.emit_order_request)

        # Add widgets to the Buy tab layout
        buy_tab_layout.addLayout(buy_form_layout)
        buy_tab_layout.addWidget(self.buy_place_order_button)
        buy_tab.setLayout(buy_tab_layout)

        # Layout for the Sell tab
        sell_tab_layout = QVBoxLayout()
        sell_form_layout = QFormLayout()

        # Sell Price input
        self.sell_price_input = QLineEdit()
        self.sell_price_input.setPlaceholderText("Enter price")
        sell_form_layout.addRow("Price:", self.sell_price_input)

        # Sell Quantity input
        self.sell_quantity_input = QLineEdit()
        self.sell_quantity_input.setPlaceholderText("Enter quantity")
        sell_form_layout.addRow("Quantity:", self.sell_quantity_input)

        # Execute Sell order button
        self.sell_place_order_button = QPushButton("Place Sell Order")
        self.sell_place_order_button.clicked.connect(self.emit_order_request)

        # Add widgets to the Sell tab layout
        sell_tab_layout.addLayout(sell_form_layout)
        sell_tab_layout.addWidget(self.sell_place_order_button)
        sell_tab.setLayout(sell_tab_layout)

        # Add tabs to the TabWidget
        self.buy_sell_tabs.addTab(buy_tab, "Buy")
        self.buy_sell_tabs.addTab(sell_tab, "Sell")

        # Set custom colors for tabs
        self.buy_sell_tabs.tabBar().setStyleSheet("""
            QTabBar::tab {
                background-color: #1E1E1E;
                color: #FFFFFF;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background-color: #333333;
                color: #FFFFFF;
            }
            QTabBar::tab:first {
                color: green; /* Buy tab */
            }
            QTabBar::tab:last {
                color: red; /* Sell tab */
            }
        """)

        # Right side: Open orders list
        self.order_book = QTableWidget()
        self.order_book.setColumnCount(2)  # Columns for Price and Qty
        self.order_book.setHorizontalHeaderLabels(["Price", "Qty"])
        self.order_book.setSortingEnabled(False)  # Allow sorting by clicking headers

        right_side_layout = QVBoxLayout()
        self.order_book_label = QLabel("Order Book")
        right_side_layout.addWidget(self.order_book_label)
        right_side_layout.addWidget(self.order_book)

        # Splitter for resizing (horizontal)
        splitter_H = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(QVBoxLayout())
        left_widget.layout().addWidget(self.buy_sell_tabs)
        right_widget = QWidget()
        right_widget.setLayout(right_side_layout)

        splitter_H.addWidget(left_widget)
        splitter_H.addWidget(right_widget)

        # Set proportional sizes using stretch factors
        splitter_H.setStretchFactor(0, 3)  # Left widget takes 3 parts of 4
        splitter_H.setStretchFactor(1, 1)  # Right widget takes 1 part of 4

        self.orders_list = QListWidget()
        self.orders_list_label = QLabel("My Open Orders")
        orders_layout = QVBoxLayout()
        orders_layout.addWidget(self.orders_list_label)
        orders_layout.addWidget(self.orders_list)

        # Splitter for resizing (vertical)
        splitter_V = QSplitter(Qt.Vertical)
        splitter_V.addWidget(splitter_H)
        lower_widget = QWidget()
        lower_widget.setLayout(orders_layout)

        splitter_V.addWidget(lower_widget)

        # Set proportional sizes using stretch factors
        splitter_V.setStretchFactor(0, 3)  # Upper widget takes 3 parts of 4
        splitter_V.setStretchFactor(1, 1)  # Lower widget takes 1 part of 4

        # Add the splitter to the main layout
        main_layout.addWidget(splitter_V)
   
    def apply_dark_mode_to_tab(self):
        """
        Apply dark mode styles to the tab components.
        """
        dark_stylesheet = """
        QWidget {
            background-color: #121212;
            color: #FFFFFF;
        }
        QLineEdit {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #333333;
            border-radius: 4px;
            padding: 4px;
        }
        QPushButton {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #444444;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
        QLabel {
            color: #FFFFFF;
        }
        QTableWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #333333;
            gridline-color: #444444;
        }
        QHeaderView::section {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #444444;
        }
        QTabWidget::pane {
            border: 1px solid #333333;
        }
        QTabBar::tab {
            background-color: #1E1E1E;
            color: #FFFFFF;
            padding: 6px;
        }
        QTabBar::tab:selected {
            background-color: #333333;
            color: #FFFFFF;
        }
        QListWidget {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #333333;
        }
        """
        self.setStyleSheet(dark_stylesheet)

    def update(self, open_orders=None, order_book_data=None):
        """
        Update the tab's content using the provided data.
        """
        if order_book_data == None:
            bids=[]
            asks=[]
            self.order_book.setVisible(False)
            self.order_book_label.setVisible(False)
        else:
            self.order_book.setVisible(True)
            self.order_book_label.setVisible(True)
            
            # Extract and sort data
            bids = sorted(order_book_data['bids'], key=lambda x: float(x[0]), reverse=True)  # Descending prices
            asks = sorted(order_book_data['asks'], key=lambda x: float(x[0]))  # Ascending prices

            bids=bids[len(bids)-5:]
            asks=asks[len(asks)-5:]

        self.order_book.setRowCount(10)
        row=0
        color=QColor("green")
        for bid in bids:
            item_bid_price = QTableWidgetItem(bid[0])
            item_bid_price.setForeground(color)  
            item_bid_qty = QTableWidgetItem(bid[1])
            item_bid_qty.setForeground(color)  
            self.order_book.setItem(row, 0, item_bid_price)
            self.order_book.setItem(row, 1, item_bid_qty)
            row+=1
            
        color=QColor("red")
        for ask in asks:
            item_ask_price = QTableWidgetItem(ask[0])
            item_ask_price.setForeground(color)  
            item_ask_qty = QTableWidgetItem(ask[1])
            item_ask_qty.setForeground(color)  
            self.order_book.setItem(row, 0, item_ask_price)
            self.order_book.setItem(row, 1, item_ask_qty)
            row+=1

        # Resize columns to fit contents
        self.order_book.resizeColumnsToContents()
        
        # Update my orders
        self.orders_list.clear()
        if(len(open_orders)):
            for order in open_orders:
                item = f"{order['side']} | Price: {order['price']} | Qty: {order['origQty']}"
                self.orders_list.addItem(item)
        else:
            self.orders_list.addItem("None open orders")

    def emit_order_request(self):
        """
        Emits the `order_requested` signal with order details when the Place Order button is clicked.
        """
        # Check which tab is currently selected: Buy (index 0) or Sell (index 1)
        if self.buy_sell_tabs.currentIndex() == 0:  # Buy tab selected
            side = "BUY"
            price = self.buy_price_input.text()  # Get price from Buy tab
            quantity = self.buy_quantity_input.text()  # Get quantity from Buy tab
        else:  # Sell tab selected
            side = "SELL"
            price = self.sell_price_input.text()  # Get price from Sell tab
            quantity = self.sell_quantity_input.text()  # Get quantity from Sell tab

        # Ensure the inputs are valid
        if not price or not quantity:
            self.logger.warning("Price or quantity is missing!")
            return

        try:
            # Prepare the order details to emit
            order_details = {
                "side": side,  # Buy or Sell
                "price": price,  # Price for the order
                "quantity": quantity  # Quantity for the order
            }

            # Emit the order_requested signal with the order details
            self.order_requested.emit(order_details)

            # Optionally, you could log the order request
            self.logger.info(f"Order requested by UI: {side} {quantity} @ {price}")

        except Exception as e:
            # Handle any exceptions and log the error
            self.logger.error(f"Failed to emit order request: {e}")


class BalanceTab(QWidget):
    """
    A tab to display the user's current spot balance.
    """
    def __init__(self, logger=None):
        super().__init__()

        if logger==None:
            self.logger = setup_logger()
        else:
            self.logger = logger
        
        # Initialize ui
        self.init_ui()

        # Apply Dark mode 
        self.apply_dark_mode_to_tab()

    def init_ui(self):
        """
        Initialize the UI components for the Balance tab.
        """
        layout = QVBoxLayout(self)

        # Title
        self.balance_label = QLabel("Spot Balances")
        layout.addWidget(self.balance_label)

        # Balance Table
        self.balance_table = QTableWidget(self)
        self.balance_table.setColumnCount(2)  # Asset and Balance
        self.balance_table.setHorizontalHeaderLabels(["Asset", "Balance"])
        layout.addWidget(self.balance_table)

        # Set custom row height and column width for better readability
        self.balance_table.verticalHeader().setDefaultSectionSize(30)  # Row height
        self.balance_table.horizontalHeader().setStretchLastSection(True)  # Stretch the last column

        # Set layout
        self.setLayout(layout)

    def apply_dark_mode_to_tab(self):
        """
        Apply dark mode styles to the Balance tab.
        """
        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: gray;
                border: 1px solid gray;
            }
            QTableWidget::item {
                background-color: #2b2b2b;
                color: white;
            }
            QHeaderView::section {
                background-color: #3b3b3b;
                color: white;
                padding: 4px;
                border: 1px solid gray;
            }
        """)

    def update(self, balances):
        """
        Update the balance table with the provided balances.

        Args:
            balances (dict): A dictionary where the keys are asset symbols (e.g., "BTC")
                            and the values are their respective balances.
        """
        try:
            self.balance_table.setRowCount(len(balances))  # Set row count

            for row, (asset, balance) in enumerate(balances.items()):
                self.balance_table.setItem(row, 0, QTableWidgetItem(asset))  # Asset
                self.balance_table.setItem(row, 1, QTableWidgetItem(str(balance)))  # Balance
            
            self.logger.info(f"Balance table updated.")

        except Exception as e:
            self.logger.error(f"Error updating balances: {e}")
            