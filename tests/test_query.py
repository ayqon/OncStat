"""
Test: Database Queries and Filtering

Verifies:
- Sarcoma filtering returns correct subset (C49, C40, C41)
- Filter by demographics works
- Summary aggregations work
"""

import pytest


class TestSarcomaFiltering:
    """Tests for sarcoma-specific filtering."""
    
    def test_filter_sarcoma_only(self, temp_db_with_data):
        """Filtering for sarcoma should return only C49/C40/C41."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence WHERE is_sarcoma = 1")
        results = cur.fetchall()
        
        assert len(results) == 3  # C49 x2, C40 x1 from fixture
        for row in results:
            assert row['icd10_code'] in ('C49', 'C40', 'C41')
    
    def test_filter_non_sarcoma(self, temp_db_with_data):
        """Non-sarcoma records should be excluded when filtering."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence WHERE is_sarcoma = 0")
        results = cur.fetchall()
        
        assert len(results) == 2  # C50, C34 from fixture


class TestFilterByICD10:
    """Tests for ICD-10 code filtering."""
    
    def test_filter_by_exact_code(self, temp_db_with_data):
        """Filter by exact ICD-10 code."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT * FROM incidence WHERE icd10_code = 'C49'")
        results = cur.fetchall()
        
        assert len(results) == 2
        assert all(r['icd10_code'] == 'C49' for r in results)


class TestSummaryQueries:
    """Tests for aggregation and summary queries."""
    
    def test_count_total(self, temp_db_with_data):
        """Count total records."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT COUNT(*) as total FROM incidence")
        result = cur.fetchone()
        
        assert result['total'] == 5
    
    def test_sum_cases(self, temp_db_with_data):
        """Sum of case counts."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT SUM(count) as total_cases FROM incidence")
        result = cur.fetchone()
        
        # 125 + 98 + 23 + 3500 + 2100 = 5846
        assert result['total_cases'] == 5846
    
    def test_mean_count(self, temp_db_with_data):
        """Mean of case counts."""
        conn, _ = temp_db_with_data
        
        cur = conn.execute("SELECT AVG(count) as avg_cases FROM incidence")
        result = cur.fetchone()
        
        # 5846 / 5 = 1169.2
        assert abs(result['avg_cases'] - 1169.2) < 0.1
