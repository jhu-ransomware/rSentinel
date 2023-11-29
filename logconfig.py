import logging
from colorama import Fore, Style, init

init()

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    RED = Fore.RED
    RESET = Style.RESET_ALL
    FORMAT = "%(asctime)s - %(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: RESET + FORMAT,
        logging.INFO: RESET + FORMAT,
        logging.WARNING: RESET + FORMAT,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        formatted_record = formatter.format(record)
        return formatted_record + self.RESET

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check if the logger already has handlers to avoid duplicate messages
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)

    return logger
