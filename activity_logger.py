"""
Activity Logger Module

Provides centralized logging for all user activities and system operations.
Dual output: File + Console.
"""

import logging
import os
from datetime import datetime
from typing import Optional

# =============================================================================
# Configuration
# =============================================================================

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'activity.log')
LOG_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s | %(message)s'

# Ensure logs directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# =============================================================================
# Logger Setup
# =============================================================================

def setup_logger(name: str = 'activity') -> logging.Logger:
    """
    Set up and return a configured logger.
    
    Args:
        name: Logger name/identifier
        
    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
activity_logger = setup_logger('activity')


# =============================================================================
# Logging Functions
# =============================================================================

def log_action(action: str, details: Optional[str] = None) -> None:
    """
    Log a user action.
    
    Args:
        action: Action type (e.g., 'IMPORT', 'EXPORT', 'FILTER')
        details: Additional details about the action
    """
    message = f"{action}"
    if details:
        message += f" | {details}"
    activity_logger.info(message)


def log_error(action: str, error: str) -> None:
    """
    Log an error.
    
    Args:
        action: Action that caused the error
        error: Error message
    """
    activity_logger.error(f"{action} | ERROR | {error}")


def log_database_action(operation: str, table: str, record_id: Optional[int] = None) -> None:
    """
    Log a database operation.
    
    Args:
        operation: CRUD operation (CREATE, READ, UPDATE, DELETE)
        table: Table name
        record_id: Optional record ID
    """
    details = f"Table: {table}"
    if record_id:
        details += f" | ID: {record_id}"
    log_action(f"DB_{operation}", details)


def log_import(file_format: str, record_count: int) -> None:
    """Log a data import operation."""
    log_action("IMPORT", f"Format: {file_format} | Records: {record_count}")


def log_export(file_format: str, record_count: int) -> None:
    """Log a data export operation."""
    log_action("EXPORT", f"Format: {file_format} | Records: {record_count}")


def log_filter(criteria: dict) -> None:
    """Log a filter operation."""
    log_action("FILTER", f"Criteria: {criteria}")


def log_chart_generated(chart_type: str) -> None:
    """Log chart generation."""
    log_action("CHART_GENERATED", f"Type: {chart_type}")


# =============================================================================
# Activity Log Reader
# =============================================================================

def get_recent_activities(limit: int = 50) -> list:
    """
    Get recent activities from log file.
    
    Args:
        limit: Maximum number of activities to return
        
    Returns:
        List of activity log entries (newest first)
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        
        # Return last N lines, reversed (newest first)
        return [line.strip() for line in lines[-limit:][::-1]]
    except Exception:
        return []
