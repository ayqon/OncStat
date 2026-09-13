"""
ETL (Extract, Transform, Load) Module

Handles data extraction from CSV, transformation (cleaning, type conversion,
sarcoma flagging), and loading into the SQLite database.

Author: Cancer Dashboard Project
Version: 1.0.0
"""

import os
from typing import Callable

import pandas as pd

from db_utils import get_db_connection, init_db


# =============================================================================
# Configuration
# =============================================================================

CSV_PATH = "data/raw/Table_2_cancer_incidence_by_icd10_2023.csv"

# ICD-10 codes for sarcoma types
SARCOMA_PREFIXES = ('C49', 'C40', 'C41')


# =============================================================================
# Data Transformation Functions
# =============================================================================

def is_sarcoma(icd10_code: str) -> bool:
    """
    Check if an ICD-10 code represents a sarcoma.
    
    Args:
        icd10_code: ICD-10 classification code
        
    Returns:
        True if code is soft tissue sarcoma (C49) or bone sarcoma (C40-C41)
    """
    if not isinstance(icd10_code, str):
        return False
    code = icd10_code.upper().strip()
    return code.startswith(SARCOMA_PREFIXES)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names for internal consistency.
    
    Args:
        df: DataFrame with original column names
        
    Returns:
        DataFrame with standardized column names
    """
    column_mapping = {
        'diagnosisyear': 'diagnosis_year',
        'age_at_diagnosis': 'age_group'
    }
    return df.rename(columns=column_mapping)


def clean_count_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and convert the count column to integers.
    
    Handles non-numeric values by converting to 0.
    
    Args:
        df: DataFrame with count column
        
    Returns:
        DataFrame with cleaned count column
    """
    df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0).astype(int)
    return df


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with missing essential data.
    
    Args:
        df: DataFrame to clean
        
    Returns:
        DataFrame with invalid rows removed
    """
    return df.dropna(subset=['icd10_code', 'diagnosis_year'])


def add_sarcoma_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add boolean column indicating if record is sarcoma.
    
    Args:
        df: DataFrame with icd10_code column
        
    Returns:
        DataFrame with is_sarcoma column added
    """
    df['is_sarcoma'] = df['icd10_code'].apply(is_sarcoma)
    return df


def select_db_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select only the columns needed for database insertion.
    
    Args:
        df: Full DataFrame
        
    Returns:
        DataFrame with only database columns
    """
    required_columns = [
        'icd10_code', 
        'diagnosis_year', 
        'gender', 
        'age_group', 
        'count', 
        'is_sarcoma'
    ]
    return df[required_columns]


# =============================================================================
# ETL Pipeline
# =============================================================================

def extract_data(file_path: str) -> pd.DataFrame:
    """
    Extract data from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Raw DataFrame from CSV
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")
    
    print(f"Reading {file_path}...")
    return pd.read_csv(file_path)


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all transformation steps to the data.
    
    Steps:
    1. Normalize column names
    2. Clean count column
    3. Remove invalid rows
    4. Add sarcoma flag
    5. Select database columns
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Transformed DataFrame ready for loading
    """
    # Apply transformations in sequence
    df = normalize_column_names(df)
    df = clean_count_column(df)
    df = remove_invalid_rows(df)
    df = add_sarcoma_flag(df)
    df = select_db_columns(df)
    
    return df


def load_data(df: pd.DataFrame) -> int:
    """
    Load transformed data into the database.
    
    Clears existing data before loading to ensure consistency.
    
    Args:
        df: Transformed DataFrame
        
    Returns:
        Number of records loaded
    """
    print(f"Loading {len(df)} records into database...")
    
    # Convert DataFrame to list of dictionaries for inspection/debugging
    records_as_dicts = df.to_dict('records')
    print(f"Sample record as dict: {records_as_dicts[0] if records_as_dicts else 'No records'}")
    
    conn = get_db_connection()
    try:
        # Clear existing data while preserving schema
        conn.execute("DELETE FROM incidence")
        conn.execute("DELETE FROM sqlite_sequence WHERE name='incidence'")
        
        # Insert new data
        df.to_sql('incidence', conn, if_exists='append', index=False)
        conn.commit()
        
        return len(df)
    finally:
        conn.close()


def run_etl() -> None:
    """
    Execute the complete ETL pipeline.
    
    Steps:
    1. Initialize database
    2. Extract data from CSV
    3. Transform data
    4. Load into database
    """
    print("Starting ETL process...")
    
    # Initialize database schema
    init_db()
    
    # Extract
    raw_df = extract_data(CSV_PATH)
    
    # Transform
    clean_df = transform_data(raw_df)
    
    # Load
    record_count = load_data(clean_df)
    
    print(f"ETL Complete. Loaded {record_count} records.")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    run_etl()
