"""
Test: Data Loader (ETL Load Phase)

Tests loading data into the SQLite database.
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataLoading:
    """Tests for loading data into database."""
    
    def test_insert_dataframe(self, temp_db):
        """Should insert DataFrame records into database."""
        conn, db_path = temp_db
        
        # Create sample DataFrame
        df = pd.DataFrame({
            'icd10_code': ['C49', 'C50'],
            'diagnosis_year': [2023, 2023],
            'gender': ['Male', 'Female'],
            'age_group': ['50-54', '55-59'],
            'count': [100, 200],
            'is_sarcoma': [True, False]
        })
        
        # Use pandas to_sql
        df.to_sql('incidence', conn, if_exists='append', index=False)
        conn.commit()
        
        # Verify
        cur = conn.execute("SELECT COUNT(*) FROM incidence")
        count = cur.fetchone()[0]
        
        assert count == 2
    
    def test_load_preserves_data(self, temp_db):
        """Loading should preserve all data values."""
        conn, db_path = temp_db
        
        df = pd.DataFrame({
            'icd10_code': ['C49.1'],
            'diagnosis_year': [2022],
            'gender': ['Female'],
            'age_group': ['60-64'],
            'count': [150],
            'is_sarcoma': [True]
        })
        
        df.to_sql('incidence', conn, if_exists='append', index=False)
        conn.commit()
        
        cur = conn.execute("SELECT * FROM incidence WHERE icd10_code = 'C49.1'")
        row = cur.fetchone()
        
        assert row['diagnosis_year'] == 2022
        assert row['gender'] == 'Female'
        assert row['count'] == 150


class TestDataRetrieval:
    """Tests for retrieving data from database."""
    
    def test_read_all_records(self, temp_db_with_data):
        """Should read all records from database."""
        conn, _ = temp_db_with_data
        
        df = pd.read_sql("SELECT * FROM incidence", conn)
        
        assert len(df) == 5  # 5 records in fixture
        assert 'icd10_code' in df.columns
    
    def test_read_with_filter(self, temp_db_with_data):
        """Should support SQL filtering."""
        conn, _ = temp_db_with_data
        
        df = pd.read_sql(
            "SELECT * FROM incidence WHERE is_sarcoma = 1", 
            conn
        )
        
        assert len(df) == 3  # 3 sarcoma records in fixture


class TestToDict:
    """Tests verifying dataframe to dictionary serialization."""
    
    def test_dataframe_to_dict_records(self, temp_db_with_data):
        """Test converting dataframe to dictionary records."""
        conn, _ = temp_db_with_data
        
        df = pd.read_sql("SELECT * FROM incidence LIMIT 3", conn)
        
        # Convert to list of dictionaries
        records = df.to_dict('records')
        
        # Verify structure
        assert isinstance(records, list)
        assert len(records) == 3
        assert isinstance(records[0], dict)
        assert 'icd10_code' in records[0]
        assert 'count' in records[0]
    
    def test_dict_has_expected_keys(self, temp_db_with_data):
        """Each record dict should have expected keys."""
        conn, _ = temp_db_with_data
        
        df = pd.read_sql("SELECT * FROM incidence LIMIT 1", conn)
        record = df.to_dict('records')[0]
        
        expected_keys = ['icd10_code', 'diagnosis_year', 'gender', 
                        'age_group', 'count', 'is_sarcoma']
        
        for key in expected_keys:
            assert key in record
