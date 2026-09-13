"""
Test: CRUD Operations

Verifies:
- Create new records
- Read existing records
- Update records
- Delete records
"""

import pytest


class TestCreate:
    """Tests for creating records."""
    
    def test_insert_record(self, temp_db):
        """Insert a new record."""
        conn, _ = temp_db
        
        conn.execute("""
            INSERT INTO incidence 
            (icd10_code, diagnosis_year, gender, age_group, count, is_sarcoma)
            VALUES ('C49.1', 2023, 'Male', '40-44', 50, 1)
        """)
        conn.commit()
        
        cur = conn.execute("SELECT * FROM incidence WHERE icd10_code = 'C49.1'")
        result = cur.fetchone()
        
        assert result is not None
        assert result['count'] == 50


class TestRead:
    """Tests for reading records."""
    
    def test_read_all(self, temp_db_with_data):
        """Read all records."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence")
        results = cur.fetchall()
        
        assert len(results) == 5


class TestUpdate:
    """Tests for updating records."""
    
    def test_update_count(self, temp_db_with_data):
        """Update the count field."""
        conn, _ = temp_db_with_data
        
        conn.execute("UPDATE incidence SET count = 999 WHERE id = 1")
        conn.commit()
        
        cur = conn.execute("SELECT count FROM incidence WHERE id = 1")
        result = cur.fetchone()
        
        assert result['count'] == 999


class TestDelete:
    """Tests for deleting records."""
    
    def test_delete_by_id(self, temp_db_with_data):
        """Delete a record by ID."""
        conn, _ = temp_db_with_data
        
        before = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
        
        conn.execute("DELETE FROM incidence WHERE id = 1")
        conn.commit()
        
        after = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
        
        assert after == before - 1
