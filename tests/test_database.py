"""
Test: Database Operations

Tests SQLite database operations including:
- Schema initialization
- CRUD operations
- Query functions
"""

import pytest
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseSchema:
    """Tests for database schema."""
    
    def test_incidence_table_exists(self, temp_db):
        """incidence table should exist."""
        conn, _ = temp_db
        
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='incidence'"
        )
        result = cur.fetchone()
        
        assert result is not None
    
    def test_table_has_expected_columns(self, temp_db):
        """Table should have all required columns."""
        conn, _ = temp_db
        
        cur = conn.execute("PRAGMA table_info(incidence)")
        columns = [row[1] for row in cur.fetchall()]
        
        expected = ['id', 'icd10_code', 'diagnosis_year', 'gender', 
                   'age_group', 'count', 'is_sarcoma']
        
        for col in expected:
            assert col in columns


class TestCRUDCreate:
    """Tests for CREATE operations."""
    
    def test_insert_single_record(self, temp_db):
        """Should insert a single record."""
        conn, _ = temp_db
        
        conn.execute("""
            INSERT INTO incidence 
            (icd10_code, diagnosis_year, gender, age_group, count, is_sarcoma)
            VALUES ('C49', 2023, 'Male', '50-54', 100, 1)
        """)
        conn.commit()
        
        cur = conn.execute("SELECT COUNT(*) FROM incidence")
        assert cur.fetchone()[0] == 1
    
    def test_insert_multiple_records(self, temp_db):
        """Should insert multiple records."""
        conn, _ = temp_db
        
        records = [
            ('C49', 2023, 'Male', '50-54', 100, 1),
            ('C50', 2023, 'Female', '55-59', 200, 0),
            ('C40', 2023, 'Male', '15-19', 50, 1),
        ]
        
        conn.executemany("""
            INSERT INTO incidence 
            (icd10_code, diagnosis_year, gender, age_group, count, is_sarcoma)
            VALUES (?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()
        
        cur = conn.execute("SELECT COUNT(*) FROM incidence")
        assert cur.fetchone()[0] == 3


class TestCRUDRead:
    """Tests for READ operations."""
    
    def test_select_all(self, temp_db_with_data):
        """Should select all records."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence")
        results = cur.fetchall()
        
        assert len(results) == 5
    
    def test_select_by_icd10(self, temp_db_with_data):
        """Should filter by ICD-10 code."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence WHERE icd10_code = 'C49'")
        results = cur.fetchall()
        
        assert len(results) == 2
        assert all(r['icd10_code'] == 'C49' for r in results)
    
    def test_select_sarcoma_only(self, temp_db_with_data):
        """Should filter sarcoma records."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence WHERE is_sarcoma = 1")
        results = cur.fetchall()
        
        assert len(results) == 3


class TestCRUDUpdate:
    """Tests for UPDATE operations."""
    
    def test_update_count(self, temp_db_with_data):
        """Should update count field."""
        conn, _ = temp_db_with_data
        
        conn.execute("UPDATE incidence SET count = 999 WHERE id = 1")
        conn.commit()
        
        cur = conn.execute("SELECT count FROM incidence WHERE id = 1")
        assert cur.fetchone()[0] == 999
    
    def test_update_does_not_affect_others(self, temp_db_with_data):
        """Update should only affect target record."""
        conn, _ = temp_db_with_data
        
        original = conn.execute("SELECT count FROM incidence WHERE id = 2").fetchone()[0]
        
        conn.execute("UPDATE incidence SET count = 999 WHERE id = 1")
        conn.commit()
        
        after = conn.execute("SELECT count FROM incidence WHERE id = 2").fetchone()[0]
        assert original == after


class TestCRUDDelete:
    """Tests for DELETE operations."""
    
    def test_delete_single_record(self, temp_db_with_data):
        """Should delete a single record."""
        conn, _ = temp_db_with_data
        
        before = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
        
        conn.execute("DELETE FROM incidence WHERE id = 1")
        conn.commit()
        
        after = conn.execute("SELECT COUNT(*) FROM incidence").fetchone()[0]
        assert after == before - 1
    
    def test_deleted_record_not_found(self, temp_db_with_data):
        """Deleted record should not be found."""
        conn, _ = temp_db_with_data
        
        conn.execute("DELETE FROM incidence WHERE id = 1")
        conn.commit()
        
        cur = conn.execute("SELECT * FROM incidence WHERE id = 1")
        assert cur.fetchone() is None


class TestAggregations:
    """Tests for summary/aggregation queries."""
    
    def test_count_total(self, temp_db_with_data):
        """Should count total records."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT COUNT(*) as total FROM incidence")
        assert cur.fetchone()['total'] == 5
    
    def test_sum_counts(self, temp_db_with_data):
        """Should sum case counts."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT SUM(count) as total FROM incidence")
        # 125 + 98 + 23 + 3500 + 2100 = 5846
        assert cur.fetchone()['total'] == 5846
    
    def test_average_count(self, temp_db_with_data):
        """Should calculate average."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT AVG(count) as avg FROM incidence")
        avg = cur.fetchone()['avg']
        assert abs(avg - 1169.2) < 0.1
    
    def test_min_max(self, temp_db_with_data):
        """Should find min and max."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT MIN(count) as min, MAX(count) as max FROM incidence")
        row = cur.fetchone()
        assert row['min'] == 23
        assert row['max'] == 3500
