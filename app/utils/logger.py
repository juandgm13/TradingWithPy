import logging
import sys
import os

# Global variables to control the verbosity level and where to log
verbose_level = 1       # Global variable to control the verbosity level (0: DEBUG, 1: INFO, 2: WARNING, 3: ERROR)
log_to_terminal = True  # Whether to log to terminal (stdout)
log_to_file = False      # Whether to log to a file (app.log)
log_file_path = "logs/app.log"  # Specify the desired log file location

# Create the logs directory if it doesn't exist
if log_to_file and not os.path.exists(os.path.dirname(log_file_path)):
    os.makedirs(os.path.dirname(log_file_path))

# Set up logging
def setup_logger():
    # Log levels mapping
    log_levels = {
        0: logging.DEBUG,
        1: logging.INFO,
        2: logging.WARNING,
        3: logging.ERROR
    }
    
    level = log_levels.get(verbose_level, logging.INFO)  # Default to INFO if invalid level

    # Create the logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # Add terminal logging handler
    if log_to_terminal:
        terminal_handler = logging.StreamHandler(sys.stdout)
        terminal_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        terminal_handler.setFormatter(formatter)
        logger.addHandler(terminal_handler)

    # Add file logging handler
    if log_to_file:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

