"""
VAPOR Cross-Platform Logging System
Professional logging with rotation and cross-platform support
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from vapor_paths import vapor_paths

class VaporLogger:
    """Professional logging system for VAPOR"""
    
    def __init__(self):
        self.logger = None
        self.setup_logging()
    
    def setup_logging(self):
        """Set up logging with rotation and proper formatting"""
        # Create logger
        self.logger = logging.getLogger('VAPOR')
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # Console handler (for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            log_file = vapor_paths.logs_dir / "vapor.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Warning: Could not set up file logging: {e}")
    
    def log(self, level, message):
        """Log a message at the specified level"""
        if self.logger:
            self.logger.log(level, message)
        else:
            print(f"{level}: {message}")

# Global logger instance
_vapor_logger = VaporLogger()

def log_startup(app_info):
    """Log application startup"""
    _vapor_logger.log(logging.INFO, "=" * 60)
    _vapor_logger.log(logging.INFO, f"VAPOR STARTUP: {app_info}")
    _vapor_logger.log(logging.INFO, f"Platform: {vapor_paths.platform}")
    _vapor_logger.log(logging.INFO, f"Data Directory: {vapor_paths.base_data_dir}")
    _vapor_logger.log(logging.INFO, "=" * 60)

def log_shutdown():
    """Log application shutdown"""
    _vapor_logger.log(logging.INFO, "VAPOR SHUTDOWN")
    _vapor_logger.log(logging.INFO, "=" * 60)

def log_info(message):
    """Log an info message"""
    _vapor_logger.log(logging.INFO, message)

def log_warning(message):
    """Log a warning message"""
    _vapor_logger.log(logging.WARNING, message)

def log_error(message):
    """Log an error message"""
    _vapor_logger.log(logging.ERROR, message)

def log_exception(message):
    """Log an exception with traceback"""
    _vapor_logger.log(logging.ERROR, message)
    if _vapor_logger.logger:
        _vapor_logger.logger.exception("Exception details:")

def log_debug(message):
    """Log a debug message"""
    _vapor_logger.log(logging.DEBUG, message)

def get_log_file_path():
    """Get the path to the current log file"""
    return vapor_paths.logs_dir / "vapor.log"
