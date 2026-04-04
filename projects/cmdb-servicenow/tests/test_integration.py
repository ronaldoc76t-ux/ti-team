"""Integration tests with ServiceNow mocks."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import responses


class TestServiceNowIntegration:
    """Integration tests with mocked ServiceNow API."""
    
    @responses.activate
    def test_create_record(self):
        """Test creating a CMDB record."""
        from servicenow.client import ServiceNowClient
        
        # Mock the API response
        responses.add(
            responses.POST,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={'result': {'sys_id': '12345'}},
            status=201
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        sys_id = client.create('cmdb_ci_server', {'name': 'test-server'})
        
        assert sys_id == '12345'
    
    @responses.activate
    def test_update_record(self):
        """Test updating a CMDB record."""
        from servicenow.client import ServiceNowClient
        
        responses.add(
            responses.PATCH,
            'https://test.service-now.com/api/now/table/cmdb_ci_server/12345',
            json={'result': {'sys_id': '12345'}},
            status=200
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        result = client.update('cmdb_ci_server', '12345', {'name': 'updated'})
        
        assert result is True
    
    @responses.activate
    def test_query_records(self):
        """Test querying CMDB records."""
        from servicenow.client import ServiceNowClient
        
        responses.add(
            responses.GET,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={
                'result': [
                    {'sys_id': '1', 'name': 'server1'},
                    {'sys_id': '2', 'name': 'server2'}
                ]
            },
            status=200
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        results = client.query('cmdb_ci_server')
        
        assert len(results) == 2
        assert results[0]['name'] == 'server1'
    
    @responses.activate
    def test_upsert_new_record(self):
        """Test upsert when record doesn't exist."""
        from servicenow.client import ServiceNowClient
        
        # First query returns empty
        responses.add(
            responses.GET,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={'result': []},
            status=200
        )
        
        # Then create
        responses.add(
            responses.POST,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={'result': {'sys_id': '67890'}},
            status=201
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        sys_id = client.upsert('cmdb_ci_server', 'new-server', {'name': 'new-server'})
        
        assert sys_id == '67890'
    
    @responses.activate
    def test_upsert_existing_record(self):
        """Test upsert when record exists."""
        from servicenow.client import ServiceNowClient
        
        # First query returns existing record
        responses.add(
            responses.GET,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={'result': [{'sys_id': '11111', 'name': 'existing'}]},
            status=200
        )
        
        # Then update
        responses.add(
            responses.PATCH,
            'https://test.service-now.com/api/now/table/cmdb_ci_server/11111',
            json={'result': {'sys_id': '11111'}},
            status=200
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        sys_id = client.upsert('cmdb_ci_server', 'existing', {'name': 'existing-updated'})
        
        assert sys_id == '11111'
    
    @responses.activate
    def test_connection_test(self):
        """Test connection to ServiceNow."""
        from servicenow.client import ServiceNowClient
        
        responses.add(
            responses.GET,
            'https://test.service-now.com/api/now/table/cmdb_ci_server',
            json={'result': []},
            status=200
        )
        
        client = ServiceNowClient('test', 'user', 'pass')
        assert client.test_connection() is True


class TestFullDiscoveryCycle:
    """Test full discovery cycle."""
    
    @patch('collectors.vmware.SmartConnect')
    @patch('normalizer.transform.Normalizer')
    def test_full_cycle(self, mock_normalizer, mock_vmware):
        """Test complete discovery cycle."""
        # This would test the full main.py flow
        pass