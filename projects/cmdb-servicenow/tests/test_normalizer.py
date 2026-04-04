"""Tests for normalizer."""

import pytest
from datetime import datetime


class TestNormalizer:
    """Tests for normalizer transform."""
    
    def test_normalizer_init(self):
        """Test normalizer initialization."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        assert normalizer.discovery_date is not None
    
    def test_transform_vmware_vm(self):
        """Test VMware VM transformation."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        vm_data = {
            'name': 'test-vm',
            'uuid': '12345',
            'ip_address': '10.1.1.1',
            'mac_address': '00:11:22:33:44:55',
            'cpu': 4,
            'memory_mb': 8192,
            'disk_gb': 100,
            'os': 'Ubuntu 22.04',
            'esxi_host': 'esxi1',
            'status': 'poweredOn',
            'zone': 'ITSG-33'
        }
        
        result = normalizer._transform_vmware(vm_data)
        
        assert result['name'] == 'test-vm'
        assert result['ip_address'] == '10.1.1.1'
        assert result['_table'] == 'cmdb_ci_vm'
        assert result['discovery_source'] == 'auto_cmdb'
        assert result['memory'] == 8  # 8192 MB / 1024 = 8 GB
    
    def test_transform_vmware_powered_off(self):
        """Test VMware VM transformation for powered off VM."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        vm_data = {
            'name': 'test-vm-off',
            'uuid': '12345',
            'ip_address': '',
            'cpu': 2,
            'memory_mb': 4096,
            'disk_gb': 50,
            'status': 'poweredOff',
            'zone': 'ITSG-33'
        }
        
        result = normalizer._transform_vmware(vm_data)
        
        assert result['operational_status'] == 'offline'
    
    def test_transform_openshift_pod(self):
        """Test OpenShift pod transformation."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        pod_data = {
            'type': 'pod',
            'name': 'myapp-pod',
            'namespace': 'production',
            'pod_ip': '10.244.1.5',
            'node': 'worker-1',
            'containers': [{'name': 'app', 'image': 'nginx:latest'}],
            'labels': {'app': 'myapp'},
            'status': 'Running'
        }
        
        result = normalizer._transform_openshift_pod(pod_data)
        
        assert result['name'] == 'production/myapp-pod'
        assert result['ip_address'] == '10.244.1.5'
        assert result['_table'] == 'cmdb_ci_kubernetes_pod'
    
    def test_transform_baremetal(self):
        """Test Bare Metal server transformation."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        server_data = {
            'hostname': 'server-prod-01',
            'ip_address': '10.0.10.1',
            'mac_address': '00:11:22:33:44:55',
            'manufacturer': 'Dell',
            'model': 'PowerEdge R740',
            'serial_number': 'SN123456',
            'cpu_cores': 16,
            'memory_gb': 64,
            'disk_gb': 2000,
            'os': 'RHEL 8',
            'status': 'online'
        }
        
        result = normalizer._transform_baremetal(server_data)
        
        assert result['name'] == 'server-prod-01'
        assert result['ip_address'] == '10.0.10.1'
        assert result['_table'] == 'cmdb_ci_server'
        assert result['cpu_core_count'] == 16
    
    def test_validate_record(self):
        """Test record validation."""
        from normalizer.transform import Normalizer
        
        normalizer = Normalizer()
        
        # Valid record
        valid_record = {
            'name': 'test',
            'ip_address': '10.1.1.1',
            'discovery_source': 'auto_cmdb'
        }
        assert normalizer.validate(valid_record) is True
        
        # Invalid - missing name
        invalid_record = {
            'ip_address': '10.1.1.1',
            'discovery_source': 'auto_cmdb'
        }
        assert normalizer.validate(invalid_record) is False
        
        # Invalid - empty name
        empty_record = {
            'name': '',
            'ip_address': '10.1.1.1',
            'discovery_source': 'auto_cmdb'
        }
        assert normalizer.validate(empty_record) is False