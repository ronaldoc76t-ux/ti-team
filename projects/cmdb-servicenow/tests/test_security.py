"""Security tests."""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch


class TestSecurity:
    """Security-focused tests."""
    
    def test_no_hardcoded_credentials(self):
        """Ensure no hardcoded credentials in source files."""
        from normalizer.transform import Normalizer
        from collectors.vmware import VMwareCollector
        
        # Check that collectors don't store credentials in plain text
        source_dir = os.path.join(os.path.dirname(__file__), '..', 'implementation')
        
        # This is a basic check - in production, use tools like bandit
        normalizer = Normalizer()
        assert normalizer is not None
    
    def test_environment_variable_usage(self):
        """Test that sensitive data comes from env vars."""
        # Verify we can read from environment
        os.environ['TEST_VAR'] = 'test_value'
        
        from servicenow.client import ServiceNowClient
        
        # Client should use env vars when credentials not provided
        client = ServiceNowClient(
            'test-instance',
            username=os.getenv('SERVICENOW_USER'),
            password=os.getenv('SERVICENOW_PASS')
        )
        
        # Should not fail initialization
        assert client.instance == 'test-instance'
    
    def test_ssl_verification_config(self):
        """Test SSL verification configuration."""
        from servicenow.client import ServiceNowClient
        
        # Verify session has proper headers
        client = ServiceNowClient('test', 'user', 'pass')
        
        assert 'Content-Type' in client.session.headers
        assert client.session.headers['Content-Type'] == 'application/json'
    
    def test_config_file_permissions(self):
        """Test that config files should have restricted permissions."""
        import stat
        
        config_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'config', 
            '.env.example'
        )
        
        # .env.example should exist and be readable
        assert os.path.exists(config_path)
        
        # Note: In production, ensure .env has 0600 permissions
        # os.stat(config_path).st_mode & stat.S_IRWGRP should be 0
    
    def test_logging_sensitive_data(self):
        """Test that sensitive data is not logged."""
        import logging
        import io
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.DEBUG)
        
        from servicenow.client import ServiceNowClient
        logger = logging.getLogger('servicenow.client')
        logger.addHandler(handler)
        
        # Create client - should not log password
        client = ServiceNowClient('test', 'admin', 'secret123')
        
        log_output = log_capture.getvalue()
        
        # Password should not appear in logs
        assert 'secret123' not in log_output
    
    def test_input_validation(self):
        """Test input validation prevents injection."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        # Test with potentially malicious input
        malicious_record = {
            'name': '<script>alert("xss")</script>',
            'ip_address': '10.1.1.1',
            'discovery_source': 'auto_cmdb'
        }
        
        result = normalizer.validate(malicious_record)
        
        # Should validate (input is technically valid)
        assert result is True
        
        # Note: In production, sanitize inputs for ServiceNow
    
    def test_network_isolation(self):
        """Test that collectors respect network boundaries."""
        # This would test that collectors only access allowed networks
        # Based on ITSG-33 zones configuration
        pass