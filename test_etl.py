import pytest
import os
import sqlite3
import pandas as pd
from db_utils import get_db_connection, init_db
from etl import is_sarcoma  # We'll need to expose this or test via DB

# Helper to inspect DB
def get_count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

def test_db_init():
    if os.path.exists("data/cancer_data.db"):
        os.remove("data/cancer_data.db")
    
    init_db()
    assert os.path.exists("data/cancer_data.db")
    
    conn = get_db_connection()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table_names = [t[0] for t in tables]
    assert "incidence" in table_names
    conn.close()

def test_sarcoma_logic():
    # Verify the helper logic if we import it, or just test data outcomes
    from etl import is_sarcoma
    assert is_sarcoma("C49.0") == True
    assert is_sarcoma("C49") == True
    assert is_sarcoma("C40.1") == True
    assert is_sarcoma("C41.9") == True
    assert is_sarcoma("C50") == False  # Breast cancer
    assert is_sarcoma(None) == False

def test_etl_data_loaded():
    # Assumes etl.py has been run or we run it here.
    # Ideally, we run it as part of setup or assume the environment is prepped.
    # Let's check the DB content that was loaded by the 'python etl.py' command in the workflow.
    
    conn = get_db_connection()
    count = get_count(conn, "incidence")
    assert count > 0, "Database is empty"
    
    # Check Sarcoma flag
    sarcoma_count = conn.execute("SELECT COUNT(*) FROM incidence WHERE is_sarcoma=1").fetchone()[0]
    assert sarcoma_count > 0, "No sarcomas flagged"
    
    # Check non-sarcomas exist too (since we loaded all)
    other_count = conn.execute("SELECT COUNT(*) FROM incidence WHERE is_sarcoma=0").fetchone()[0]
    assert other_count > 0
    
    conn.close()
