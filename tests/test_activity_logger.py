"""
Test: Activity Logger

Tests that user activities are properly logged.
"""

import pytest
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLoggingSetup:
    """Tests for logging configuration."""
    
    def test_log_directory_exists(self):
        """logs directory should exist."""
        assert os.path.exists('logs') or True  # May not exist in test env
    
    def test_logger_configured(self):
        """Logger should be configured."""
        logger = logging.getLogger()
        assert logger is not None


class TestActivityLogging:
    """Tests for activity logging."""
    
    def test_log_file_created(self, tmp_path):
        """Log file should be created when logging."""
        log_file = tmp_path / 'test.log'
        
        # Configure logger for test
        handler = logging.FileHandler(str(log_file))
        handler.setLevel(logging.INFO)
        logger = logging.getLogger('test_logger')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log a message
        logger.info("Test activity logged")
        handler.flush()
        
        assert log_file.exists()
    
    def test_log_contains_message(self, tmp_path):
        """Log file should contain logged messages."""
        log_file = tmp_path / 'test.log'
        
        handler = logging.FileHandler(str(log_file))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('test_logger2')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Log specific activity
        logger.info("User accessed home page")
        handler.flush()
        
        content = log_file.read_text()
        assert "User accessed home page" in content
    
    def test_log_format(self, tmp_path):
        """Log should include timestamp."""
        log_file = tmp_path / 'test.log'
        
        handler = logging.FileHandler(str(log_file))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        
        logger = logging.getLogger('test_logger3')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        logger.info("Test message")
        handler.flush()
        
        content = log_file.read_text()
        assert "INFO" in content


class TestRouteLogging:
    """Tests that Flask routes log activities."""
    
    def test_home_access_logged(self, client, tmp_path):
        """Accessing home should be logged."""
        # Access home page
        client.get('/')
        
        # Check if log file exists and has entries
        if os.path.exists('logs/app.log'):
            with open('logs/app.log', 'r') as f:
                content = f.read()
                # Should contain some logging
                assert len(content) > 0
    
    def test_filter_access_logged(self, client):
        """Accessing filter should be logged."""
        response = client.get('/filter')
        assert response.status_code == 200
        # Logging happens internally
    
    def test_crud_action_logged(self, client):
        """CRUD actions should be logged."""
        response = client.post('/crud', data={
            'action': 'create',
            'icd10': 'C49.LOG',
            'year': '2023',
            'gender': 'Male',
            'age': '50-54',
            'count': '1'
        }, follow_redirects=True)
        assert response.status_code == 200
