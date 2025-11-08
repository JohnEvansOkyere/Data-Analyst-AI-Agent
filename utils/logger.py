"""
VexaAI Data Analyst - Logging Utility
Centralized logging system for MLOps practices
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config.settings import (
    LOGS_DIR,
    ENABLE_LOGGING,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE_MAX_BYTES,
    LOG_FILE_BACKUP_COUNT
)

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "error.log"
PERFORMANCE_LOG_FILE = LOGS_DIR / "performance.log"


def setup_logger(name: str, log_level: str = LOG_LEVEL) -> logging.Logger:
    """
    Setup and configure a logger
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if logger.handlers:
        return logger
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if ENABLE_LOGGING:
        # File handler for all logs
        file_handler = RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=LOG_FILE_MAX_BYTES,
            backupCount=LOG_FILE_BACKUP_COUNT
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return setup_logger(name)


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = setup_logger("performance")
        
        if ENABLE_LOGGING:
            # Add performance-specific handler
            perf_handler = RotatingFileHandler(
                PERFORMANCE_LOG_FILE,
                maxBytes=LOG_FILE_MAX_BYTES,
                backupCount=LOG_FILE_BACKUP_COUNT
            )
            perf_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(LOG_FORMAT)
            perf_handler.setFormatter(formatter)
            self.logger.addHandler(perf_handler)
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        metadata: dict = None
    ):
        """Log a performance metric"""
        metadata_str = f" | {metadata}" if metadata else ""
        self.logger.info(
            f"Operation: {operation} | Duration: {duration:.4f}s{metadata_str}"
        )
    
    def log_data_processing(
        self,
        operation: str,
        rows_before: int,
        rows_after: int,
        duration: float
    ):
        """Log data processing metrics"""
        self.logger.info(
            f"Data Processing: {operation} | "
            f"Rows: {rows_before} → {rows_after} | "
            f"Duration: {duration:.4f}s"
        )


class AuditLogger:
    """Logger for audit trails"""
    
    def __init__(self):
        self.logger = setup_logger("audit")
        
        if ENABLE_LOGGING:
            audit_log_file = LOGS_DIR / "audit.log"
            audit_handler = RotatingFileHandler(
                audit_log_file,
                maxBytes=LOG_FILE_MAX_BYTES,
                backupCount=LOG_FILE_BACKUP_COUNT
            )
            audit_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - AUDIT - %(message)s"
            )
            audit_handler.setFormatter(formatter)
            self.logger.addHandler(audit_handler)
    
    def log_user_action(
        self,
        user_id: str,
        action: str,
        details: str = "",
        metadata: dict = None
    ):
        """Log user action for audit trail"""
        metadata_str = f" | {metadata}" if metadata else ""
        self.logger.info(
            f"User: {user_id} | Action: {action} | "
            f"Details: {details}{metadata_str}"
        )
    
    def log_data_access(
        self,
        user_id: str,
        dataset_name: str,
        access_type: str
    ):
        """Log data access"""
        self.logger.info(
            f"User: {user_id} | Dataset: {dataset_name} | "
            f"Access: {access_type}"
        )
    
    def log_export(
        self,
        user_id: str,
        dataset_name: str,
        format: str,
        rows: int
    ):
        """Log data export"""
        self.logger.info(
            f"User: {user_id} | Dataset: {dataset_name} | "
            f"Export: {format} | Rows: {rows}"
        )


# Global instances
performance_logger = PerformanceLogger()
audit_logger = AuditLogger()


def log_performance(operation: str, duration: float, metadata: dict = None):
    """Convenience function for performance logging"""
    performance_logger.log_operation(operation, duration, metadata)


def log_audit(user_id: str, action: str, details: str = "", metadata: dict = None):
    """Convenience function for audit logging"""
    audit_logger.log_user_action(user_id, action, details, metadata)
