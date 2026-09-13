"""
Pytest Configuration and Fixtures

Provides shared fixtures for isolated testing:
- Sample CSV data (no file dependency)
- Temporary SQLite database
- Flask test client with mocked DB
"""

import os
import sys
import pytest
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Sample Data (embedded - no external file dependency)
# =============================================================================

SAMPLE_CSV_CONTENT = """icd10_code,diagnosisyear,gender,age_at_diagnosis,count
C49,2023,Male,50-54,125
C49,2023,Female,50-54,98
C49,2023,Male,55-59,142
C40,2023,Male,15-19,23
C41,2023,Female,20-24,18
C50,2023,Female,50-54,3500
C34,2023,Male,65-69,2100
"""

SAMPLE_RECORDS = [
    ('C49', 2023, 'Male', '50-54', 125, 1),
    ('C49', 2023, 'Female', '50-54', 98, 1),
    ('C40', 2023, 'Male', '15-19', 23, 1),
    ('C50', 2023, 'Female', '50-54', 3500, 0),
    ('C34', 2023, 'Male', '65-69', 2100, 0),
]


# =============================================================================
# Data Fixtures
# =============================================================================

@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary sample CSV file."""
    csv_file = tmp_path / "sample_incidence.csv"
    csv_file.write_text(SAMPLE_CSV_CONTENT)
    return str(csv_file)


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary SQLite database with schema."""
    db_path = tmp_path / "test_cancer.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    # Create schema matching production
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
    
    yield conn, str(db_path)
    
    conn.close()


@pytest.fixture
def temp_db_with_data(temp_db):
    """Database pre-populated with sample data."""
    conn, db_path = temp_db
    
    conn.executemany(
        """INSERT INTO incidence 
           (icd10_code, diagnosis_year, gender, age_group, count, is_sarcoma)
           VALUES (?, ?, ?, ?, ?, ?)""",
        SAMPLE_RECORDS
    )
    conn.commit()
    
    return conn, db_path


# =============================================================================
# Flask Application Fixtures
# =============================================================================

@pytest.fixture
def client(temp_db_with_data, monkeypatch):
    """Flask test client with temporary database."""
    conn, db_path = temp_db_with_data
    
    # Monkeypatch db_utils to use temp DB
    import db_utils
    monkeypatch.setattr(db_utils, 'DB_PATH', db_path)
    
    # Import app AFTER patching
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as test_client:
        yield test_client
