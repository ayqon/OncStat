"""
Database Utilities Module

Provides database connection management and initialization for the
Cancer Data Dashboard application.

Author: Cancer Dashboard Project
Version: 1.0.0
"""

import os
import sqlite3
from typing import Optional

# =============================================================================
# Configuration
# =============================================================================

DB_PATH = "data/cancer_data.db"


# =============================================================================
# Connection Management
# =============================================================================

def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    The connection is configured with Row factory for dict-like row access.
    
    Returns:
        sqlite3.Connection: Active database connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# Database Initialization
# =============================================================================

def init_db() -> None:
    """
    Initialize the database with the required schema.
    
    Creates the data directory and incidence table if they don't exist.
    This function is idempotent - safe to call multiple times.
    """
    # Ensure data directory exists
    data_dir = os.path.dirname(DB_PATH)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Create table with schema
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                icd10_code TEXT NOT NULL,
                diagnosis_year INTEGER NOT NULL,
                gender TEXT NOT NULL,
                age_group TEXT,
                count INTEGER,
                is_sarcoma BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
    finally:
        conn.close()


def reset_db() -> None:
    """
    Reset the database by removing all records.
    
    Preserves the table schema but removes all data.
    Also resets the autoincrement counter.
    """
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM incidence")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        conn.commit()
    finally:
        conn.close()


# =============================================================================
# Entry Point (for testing)
# =============================================================================

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
