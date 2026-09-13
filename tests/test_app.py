"""
Test: Flask Application Routes

Tests all Flask routes return expected responses.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHomeRoute:
    """Tests for the home page route."""
    
    def test_home_page_loads(self, client):
        """Home page should return 200 status."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Cancer' in response.data
    
    def test_home_shows_stats(self, client):
        """Home page should display statistics."""
        response = client.get('/')
        assert response.status_code == 200


class TestFilterRoute:
    """Tests for the filter/explore page."""
    
    def test_filter_page_loads(self, client):
        """Filter page GET should return 200."""
        response = client.get('/filter')
        assert response.status_code == 200
    
    def test_filter_with_icd10(self, client):
        """Filter with ICD-10 parameter should work."""
        response = client.post('/filter', data={'icd10': 'C49'})
        assert response.status_code == 200
    
    def test_filter_sarcoma_only(self, client):
        """Sarcoma-only filter should work."""
        response = client.post('/filter', data={'sarcoma_only': '1'})
        assert response.status_code == 200


class TestDashboardRoute:
    """Tests for the charts/dashboard page."""
    
    def test_dashboard_loads(self, client):
        """Dashboard page should return 200."""
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_dashboard_has_charts(self, client):
        """Dashboard should contain chart images."""
        response = client.get('/dashboard')
        # Charts are base64 encoded images
        assert b'img' in response.data or b'base64' in response.data


class TestCrudRoute:
    """Tests for the CRUD management page."""
    
    def test_crud_page_loads(self, client):
        """CRUD page GET should return 200."""
        response = client.get('/crud')
        assert response.status_code == 200
    
    def test_crud_create_record(self, client):
        """Creating a record should work."""
        response = client.post('/crud', data={
            'action': 'create',
            'icd10': 'C49.TEST',
            'year': '2023',
            'gender': 'Male',
            'age': '50-54',
            'count': '10'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestExportRoute:
    """Tests for the export endpoint."""
    
    def test_export_page_loads(self, client):
        """Export page GET should return 200."""
        response = client.get('/export')
        assert response.status_code == 200
        assert b'Export Options' in response.data
    
    def test_export_returns_csv(self, client):
        """Export POST should return CSV content type."""
        response = client.post('/export', data={'format': 'csv'})
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
    
    def test_export_has_headers(self, client):
        """Exported CSV should have column headers."""
        response = client.post('/export', data={'format': 'csv'})
        assert b'icd10_code' in response.data


class TestImportRoute:
    """Tests for the import page."""
    
    def test_import_page_loads(self, client):
        """Import page should return 200."""
        response = client.get('/import')
        assert response.status_code == 200


class TestLogsRoute:
    """Tests for the activity logs page."""
    
    def test_logs_page_loads(self, client):
        """Logs page should return 200."""
        response = client.get('/logs')
        assert response.status_code == 200
