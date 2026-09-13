"""
BYSITE.TXT Data Loader

Loads US CDC/SEER cancer statistics from BYSITE.TXT format.
This file demonstrates loading an alternative dataset format into the same
database schema as the NHS Digital data.

Format: Pipe-delimited text file
Columns: YEAR|RACE|SEX|SITE|EVENT_TYPE|AGE_ADJUSTED_CI_LOWER|AGE_ADJUSTED_CI_UPPER|AGE_ADJUSTED_RATE|COUNT|POPULATION

Author: OncStat Project
Version: 1.0.0
"""

import pandas as pd
import sqlite3
import os
from typing import Tuple, Optional

# Database path (same as main app)
DB_PATH = "data/cancer_data.db"


def is_sarcoma_site(site: str) -> bool:
    """
    Check if a cancer site name represents sarcoma.
    
    BYSITE.TXT uses descriptive site names rather than ICD-10 codes.
    Sarcoma-related sites include:
    - "Soft Tissue including Heart" (soft tissue sarcoma)
    - "Bones and Joints" (bone sarcoma)
    
    Args:
        site: Cancer site name from BYSITE.TXT
        
    Returns:
        True if site is sarcoma-related
    """
    if not isinstance(site, str):
        return False
    site_lower = site.lower().strip()
    return 'soft tissue' in site_lower or 'bones and joints' in site_lower


def load_bysite_data(filepath: str = "BYSITE.TXT") -> pd.DataFrame:
    """
    Load and parse BYSITE.TXT data file.
    
    This function demonstrates:
    - Reading pipe-delimited text files
    - Data type conversion
    - Handling alternative column names
    
    Args:
        filepath: Path to BYSITE.TXT file
        
    Returns:
        Cleaned pandas DataFrame
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"BYSITE.TXT not found at {filepath}")
    
    # Read pipe-delimited file
    df = pd.read_csv(
        filepath, 
        delimiter='|',
        encoding='utf-8',
        dtype={'YEAR': str}  # Keep as string to handle ranges like "2018-2022"
    )
    
    # Display column info for verification
    print(f"Loaded {len(df)} rows from BYSITE.TXT")
    print(f"Columns: {list(df.columns)}")
    
    return df


def clean_bysite_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize BYSITE.TXT data for database insertion.
    
    Demonstrates:
    - Filtering out aggregate rows (year ranges)
    - Column mapping to standard schema
    - Data type conversion
    - Sarcoma flagging
    
    Args:
        df: Raw DataFrame from load_bysite_data
        
    Returns:
        Cleaned DataFrame matching incidence table schema
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Filter out aggregate year ranges (e.g., "2018-2022")
    df = df[~df['YEAR'].str.contains('-', na=False)]
    
    # Convert year to integer
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df = df.dropna(subset=['YEAR'])
    df['YEAR'] = df['YEAR'].astype(int)
    
    # Map columns to our standard schema
    df_clean = pd.DataFrame({
        'icd10_code': df['SITE'],  # Use SITE as equivalent to ICD-10 code
        'diagnosis_year': df['YEAR'],
        'gender': df['SEX'],
        'age_group': 'All ages',  # BYSITE.TXT doesn't have age breakdown
        'count': df['COUNT'],
        'is_sarcoma': df['SITE'].apply(is_sarcoma_site),
        # Additional fields from BYSITE.TXT
        'event_type': df['EVENT_TYPE'],  # Incidence or Mortality
        'race': df['RACE'],
        'age_adjusted_rate': df['AGE_ADJUSTED_RATE'],
        'population': df['POPULATION']
    })
    
    # Ensure count is numeric
    df_clean['count'] = pd.to_numeric(df_clean['count'], errors='coerce').fillna(0).astype(int)
    
    print(f"Cleaned data: {len(df_clean)} rows")
    print(f"Sarcoma records: {df_clean['is_sarcoma'].sum()}")
    
    return df_clean


def insert_bysite_to_db(df: pd.DataFrame, db_path: str = DB_PATH) -> int:
    """
    Insert BYSITE.TXT data into the incidence table.
    
    Note: This uses the same schema as NHS Digital data for compatibility.
    The SITE field is stored in icd10_code column.
    
    Args:
        df: Cleaned DataFrame from clean_bysite_data
        db_path: Path to SQLite database
        
    Returns:
        Number of records inserted
    """
    # Select only columns matching incidence table schema
    df_insert = df[['icd10_code', 'diagnosis_year', 'gender', 'age_group', 'count', 'is_sarcoma']]
    
    conn = sqlite3.connect(db_path)
    try:
        # Insert records
        df_insert.to_sql('incidence', conn, if_exists='append', index=False)
        conn.commit()
        print(f"Inserted {len(df_insert)} records into database")
        return len(df_insert)
    finally:
        conn.close()


def run_bysite_etl(filepath: str = "BYSITE.TXT") -> Tuple[bool, str]:
    """
    Run complete ETL pipeline for BYSITE.TXT data.
    
    This is the main entry point that:
    1. Loads the BYSITE.TXT file
    2. Cleans and transforms the data
    3. Inserts into the database
    
    Args:
        filepath: Path to BYSITE.TXT file
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        print("="*60)
        print("BYSITE.TXT ETL Pipeline")
        print("="*60)
        
        # Step 1: Load data
        print("\n[1/3] Loading BYSITE.TXT...")
        df_raw = load_bysite_data(filepath)
        
        # Step 2: Clean data
        print("\n[2/3] Cleaning and transforming data...")
        df_clean = clean_bysite_data(df_raw)
        
        # Step 3: Insert to database
        print("\n[3/3] Inserting into database...")
        count = insert_bysite_to_db(df_clean)
        
        print("\n" + "="*60)
        print(f"ETL Complete! Loaded {count} records from BYSITE.TXT")
        print("="*60)
        
        return True, f"Successfully loaded {count} records from BYSITE.TXT"
        
    except FileNotFoundError as e:
        return False, f"File not found: {e}"
    except Exception as e:
        return False, f"ETL failed: {str(e)}"


def get_bysite_summary(filepath: str = "BYSITE.TXT") -> dict:
    """
    Get a summary of the BYSITE.TXT data without inserting.
    
    Useful for previewing the data before import.
    
    Args:
        filepath: Path to BYSITE.TXT file
        
    Returns:
        Dictionary with data summary
    """
    df_raw = load_bysite_data(filepath)
    df_clean = clean_bysite_data(df_raw)
    
    return {
        'total_rows': len(df_clean),
        'year_range': f"{df_clean['diagnosis_year'].min()}-{df_clean['diagnosis_year'].max()}",
        'sites': df_clean['icd10_code'].nunique(),
        'sarcoma_records': int(df_clean['is_sarcoma'].sum()),
        'incidence_records': len(df_clean[df_clean['event_type'] == 'Incidence']),
        'mortality_records': len(df_clean[df_clean['event_type'] == 'Mortality']),
        'genders': list(df_clean['gender'].unique()),
        'races': list(df_clean['race'].unique())[:5]  # Show first 5
    }


# =============================================================================
# Data Serialization Utilities
# =============================================================================

def demonstrate_to_dict_records(filepath: str = "BYSITE.TXT", limit: int = 5):
    """
    Serialize DataFrame rows to a list of dictionaries.
    
    This converts a DataFrame to a list of dictionaries where each
    dictionary represents a row with column names as keys.
    
    Args:
        filepath: Path to BYSITE.TXT file
        limit: Number of records to show
        
    Returns:
        List of dictionaries representing the first N records
    """
    df_raw = load_bysite_data(filepath)
    df_clean = clean_bysite_data(df_raw)
    
    # Get sarcoma-only data and convert to list of records
    sarcoma_df = df_clean[df_clean['is_sarcoma'] == True].head(limit)
    
    # Use to_dict('records') to convert to list of dictionaries
    records_list = sarcoma_df.to_dict('records')
    
    print(f"\nDemonstrating df.to_dict('records'):")
    print(f"Converted {len(records_list)} sarcoma records to list of dictionaries")
    print("\nSample record structure:")
    if records_list:
        for key, value in records_list[0].items():
            print(f"  {key}: {value}")
    
    return records_list


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        # Preview mode - just show summary
        print("BYSITE.TXT Data Preview")
        print("-" * 40)
        summary = get_bysite_summary()
        for key, value in summary.items():
            print(f"{key}: {value}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo mode - show to_dict('records') usage
        demonstrate_to_dict_records()
    else:
        # Full ETL mode
        success, message = run_bysite_etl()
        print(f"\nResult: {message}")
        sys.exit(0 if success else 1)
