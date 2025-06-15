import logging
from pathlib import Path

import logging
from pathlib import Path

class Logger:
    def __init__(self, log_file: str = "tagoror_rag.log", log_level: int = logging.DEBUG, log_to_console: bool = True, log_path: Path = None):
        """
        Initializes the logger with the given configuration.

        Args:
            log_file (str): Name of the log file.
            log_level (int): Logging level for the logger.
            log_to_console (bool): Whether to also log to the console.
            log_path (Path): Custom path for the log directory.
        """
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(log_level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(self._create_log_file_path(log_file, log_path))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _create_log_file_path(self, log_file: str, log_path: Path) -> str:
        """
        Ensure the log directory exists and return the full log file path.

        Args:
            log_file (str): The log file name.
            log_path (Path): Custom path for the log directory.

        Returns:
            str: The full path to the log file.
        """
        log_directory = log_path if log_path else (Path.cwd().parent.parent.parent / "data/logs")
        log_directory.mkdir(parents=True, exist_ok=True)
        return str(log_directory / log_file)

    def get_logger(self) -> logging.Logger:
        """
        Returns the configured logger.

        Returns:
            logging.Logger: The configured logger instance.
        """
        return self.logger

custom_log_path = Path.cwd().parent.parent.parent
logger = Logger(log_file="tagoror_ui.log", log_path=custom_log_path).get_logger()
logger.info("Logger configured successfully with a custom path.")