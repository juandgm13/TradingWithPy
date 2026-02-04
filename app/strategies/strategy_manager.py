from app.utils.logger import setup_logger
from app.utils.GmailSender import EmailSender
from app.strategies.strategies import Strategy_class
import os
from datetime import datetime
import csv

class StrategyManager:
    def __init__(self, logger=None):
        self.strategies = {}
        self.logger = logger if logger else setup_logger()
        self.notifier = EmailSender(self.logger)
        self.logger.info("StrategyManager initialized with API Manager.")

    def register_strategy(self, name, strategy_instance):
        if isinstance(strategy_instance, Strategy_class):
            self.strategies[name] = strategy_instance
            self.logger.info(f"Strategy '{name}' registered.")
        else:
            self.logger.error("Attempted to register a strategy that does not inherit from Strategy_class.")

    def run_strategies(self):
        self.logger.info("Running strategies...")
        all_signals = []
        for strategy in self.strategies.items():
            signals = strategy.execute()
            if signals:
                all_signals.extend(signals)
        if all_signals:
            subject = "Trading Signal Alerts"
            body = ""
            attachments = []
            folder = "data"
            os.makedirs(folder, exist_ok=True)

            for signal in all_signals:
                body += f"Symbol: {signal['symbol']}, Signal: {signal['type']}, Time: {datetime.now()}, Details: {signal['details']}\n"
                csv_filename = os.path.join(folder, f"{signal['symbol']}_signal_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
                with open(csv_filename, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Time', 'Signal', 'Details', 'Market Data'])
                    writer.writerow([datetime.now(), signal['type'], signal['details'], signal['market_data']])
                attachments.append(csv_filename)

            self.notifier.send_notification(subject, body, attachments)