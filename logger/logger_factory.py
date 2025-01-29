import logging


class LoggerFactory:
    def __init__(self):
        # Formatter setup
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="[%m/%d/%Y %H:%M:%S]")

    def get_logger(self, name, log_file_path):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Remove existing handlers to prevent duplicate logs during repeated tests
        if logger.hasHandlers():
            logger.handlers.clear()

        # Create handlers
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(self.formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger