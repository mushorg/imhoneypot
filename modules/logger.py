import logging
import logging.handlers
import modules.settings
import sys

class LogThis():
    """
    Logfile and console logging class.
    """
    def __init__(self):
        """Initializing logging"""
        # Log level
        log_levels = {
          'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL
          }
        # Checks for a argument
        if len(sys.argv) > 1:
            level_name = sys.argv[1]
        else:
            # Get the log level from the settings
            level_name = "debug"
        log_level = log_levels.get(level_name, logging.NOTSET)

        # Log entry formatting
        datefmt = "%a, %d %b %Y %H:%M:%S"
        log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt)

        # Initialize the file logger
        self.file_logger = logging.getLogger('IMHoneypot File Logger')
        self.file_logger.setLevel(log_level)
        self.log_filename = "log/file/imhoneypot.log"
        # Initialize the file rotating handler
        logfile_handler = logging.handlers.RotatingFileHandler(self.log_filename, maxBytes=2097152, backupCount=5)
        logfile_handler.setFormatter(log_format)
        self.file_logger.addHandler(logfile_handler)

        # Initialize the console logger
        self.console_logger = logging.getLogger('IMHoneypot Console Logger')
        self.console_logger.setLevel(log_level)
        # Initialize the console logging handler
        logconsole_handler = logging.StreamHandler()
        logconsole_handler.setFormatter(log_format)
        self.console_logger.addHandler(logconsole_handler)

    def log_file(self, message, lvl):
        # This function logs to the logfile
        getattr(self.file_logger,lvl)(message)

    def log_console(self, message, lvl):
        # This function logs to the stream
        getattr(self.console_logger,lvl)(message)

    def log_both(self, message, lvl):
        # This function logs to the logfile and the console
        getattr(self.console_logger,lvl)(message)