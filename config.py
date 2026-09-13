"""
Configuration Module

Centralized configuration for paths, URLs, and settings.
"""

import os

# =============================================================================
# Paths
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Database
DB_PATH = os.path.join(DATA_DIR, "cancer_data.db")

# Source data - US CDC USCS Cancer Statistics 1999-2022
DATA_URL = "https://www.cdc.gov/cancer/uscs/USCS-1999-2022-ASCII.zip"
ZIP_PATH = os.path.join(DATA_DIR, "USCS_data.zip")
# Main data file in the ZIP
SOURCE_FILENAME = "BYSITE.TXT"
SOURCE_PATH = os.path.join(RAW_DIR, SOURCE_FILENAME)

# =============================================================================
# Sarcoma Configuration
# =============================================================================

# ICD-10 codes for sarcoma
SARCOMA_PREFIXES = ('C49', 'C40', 'C41')

# =============================================================================
# Logging
# =============================================================================

LOG_FILE = os.path.join(LOGS_DIR, "app.log")
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'

# =============================================================================
# Ensure directories exist
# =============================================================================

def ensure_directories():
    """Create required directories if they don't exist."""
    for directory in [DATA_DIR, RAW_DIR, LOGS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
