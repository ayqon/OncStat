"""
Test: Flask Routes (Smoke Tests)

Verifies all main routes return HTTP 200.
Run from fresh clone with: pytest -q
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHomeRoute:
    """Tests for the home page."""
    
    def test_home_returns_200(self, client):
        """Home page should return 200 status."""
        response = client.get('/')
        assert response.status_code == 200


class TestFilterRoute:
    """Tests for the filter page."""
    
    def test_filter_get_returns_200(self, client):
        """Filter page GET should return 200."""
        response = client.get('/filter')
        assert response.status_code == 200
    
    def test_filter_post_returns_200(self, client):
        """Filter page POST should return 200."""
        response = client.post('/filter', data={'icd10': 'C49'})
        assert response.status_code == 200


class TestDashboardRoute:
    """Tests for the dashboard page."""
    
    def test_dashboard_returns_200(self, client):
        """Dashboard page should return 200."""
        response = client.get('/dashboard')
        assert response.status_code == 200


class TestCrudRoute:
    """Tests for the CRUD page."""
    
    def test_crud_get_returns_200(self, client):
        """CRUD page GET should return 200."""
        response = client.get('/crud')
        assert response.status_code == 200


class TestExportRoute:
    """Tests for the export endpoint."""
    
    def test_export_get_returns_200(self, client):
        """Export page GET should return 200."""
        response = client.get('/export')
        assert response.status_code == 200
    
    def test_export_post_returns_csv(self, client):
        """Export POST should return CSV with headers."""
        response = client.post('/export', data={'format': 'csv'})
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert b'icd10_code' in response.data  # Header present
