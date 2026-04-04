"""Pytest fixtures and configuration."""

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock

# Add implementation to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'implementation'))


@pytest.fixture
def mock_vmware_config():
    """Mock VMware configuration."""
    return {
        'name': 'test-vcenter',
        'host': 'vcenter.test.com',
        'user': 'admin',
        'password': 'testpass',
        'port': 443
    }


@pytest.fixture
def mock_openshift_config():
    """Mock OpenShift configuration."""
    return {
        'name': 'test-ocp',
        'api_url': 'https://api.test.com:6443',
        'token': 'test-token',
        'verify_ssl': True
    }


@pytest.fixture
def mock_baremetal_config():
    """Mock Bare Metal configuration."""
    return {
        'target': '10.0.0.1',
        'community': 'public',
        'snmp_version': '2c'
    }


@pytest.fixture
def mock_vm_data():
    """Mock VMware VM data."""
    return {
        'name': 'test-vm',
        'uuid': '12345-67890',
        'ip_address': '10.1.1.100',
        'mac_address': '00:11:22:33:44:55',
        'cpu': 4,
        'memory_mb': 8192,
        'disk_gb': 100,
        'os': 'Ubuntu 22.04 LTS',
        'esxi_host': 'esxi1.test.com',
        'status': 'poweredOn',
        'zone': 'ITSG-33'
    }


@pytest.fixture
def mock_pod_data():
    """Mock OpenShift pod data."""
    return {
        'type': 'pod',
        'name': 'nginx-pod',
        'namespace': 'production',
        'pod_ip': '10.244.1.10',
        'node': 'worker-1',
        'containers': [
            {'name': 'nginx', 'image': 'nginx:latest', 'ports': [80]}
        ],
        'labels': {'app': 'nginx', 'environment': 'prod'},
        'status': 'Running',
        'source': 'ocp-prod'
    }


@pytest.fixture
def mock_server_data():
    """Mock bare metal server data."""
    return {
        'hostname': 'server-prod-01',
        'ip_address': '10.0.10.1',
        'mac_address': '00:11:22:33:44:66',
        'manufacturer': 'Dell',
        'model': 'PowerEdge R740',
        'serial_number': 'SN123456',
        'cpu_cores': 16,
        'memory_gb': 64,
        'disk_gb': 2000,
        'os': 'RHEL 8.5',
        'status': 'online'
    }


@pytest.fixture
def mock_servicenow_client():
    """Mock ServiceNow client."""
    from servicenow.client import ServiceNowClient
    
    client = ServiceNowClient('test', 'user', 'pass')
    
    # Mock the session
    client.session = Mock()
    client.session.post.return_value = Mock(
        status_code=201,
        json.return_value={'result': {'sys_id': '12345'}}
    )
    client.session.get.return_value = Mock(
        status_code=200,
        json.return_value={'result': []}
    )
    client.session.patch.return_value = Mock(
        status_code=200,
        json.return_value={'result': {'sys_id': '12345'}}
    )
    
    return client


@pytest.fixture
def mock_config():
    """Mock configuration."""
    return {
        'collectors': {
            'vmware': {
                'enabled': True,
                'sources': [{'name': 'vc1', 'host': 'vcenter.test.com', 'user': 'u', 'password': 'p'}]
            },
            'openshift': {
                'enabled': True,
                'sources': [{'name': 'ocp1', 'api_url': 'https://api.test.com', 'token': 't'}]
            },
            'baremetal': {
                'enabled': True,
                'targets': [{'target': '10.0.0.0/24', 'community': 'public'}]
            }
        },
        'servicenow': {
            'instance': 'test.service-now.com'
        }
    }


@pytest.fixture
def temp_env_file(tmp_path):
    """Create temporary .env file."""
    env_file = tmp_path / '.env'
    env_file.write_text('SERVICENOW_USER=test\nSERVICENOW_PASS=test\n')
    return env_file