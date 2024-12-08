from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QRadioButton
from app.ui.charts import CandlestickChart, VolumeChart, DepthChart, RSIChart
from PyQt5.QtCore import pyqtSignal
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
                self.depth_chart.update_chart(depth, rsi_period)
                self.logger.info("Depth chart updated successfully.")
            except Exception as e:
                self.logger.error(f"Failed to update depth chart: {e}")
                self.show_error_message(f"Depth chart error: {e}")
            
            # Update RSI chart if there is enough data
            try:
                if len(candlesticks) > rsi_period:  # Ensure there's enough data for the default RSI period (14)
                    closing_prices = [float(c[4]) for c in candlesticks]  # Extract closing prices
                    self.rsi_chart.update_chart(closing_prices, period=rsi_period)
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

        if new_selected_interval != self.selected_interval :
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