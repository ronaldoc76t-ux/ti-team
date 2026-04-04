"""Tests for collectors."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestVMwareCollector:
    """Tests for VMware collector."""
    
    def test_vmware_config_creation(self):
        """Test VMware config creation."""
        from collectors.vmware import VMwareConfig, VMwareCollector
        
        config = VMwareConfig(
            name="test-vcenter",
            host="vcenter.test.com",
            user="admin",
            password="pass",
            port=443
        )
        
        assert config.name == "test-vcenter"
        assert config.host == "vcenter.test.com"
    
    def test_vmware_collector_init(self):
        """Test VMware collector initialization."""
        from collectors.vmware import VMwareCollector
        
        sources = [
            {"name": "vc1", "host": "vc1.test.com", "user": "u", "password": "p"}
        ]
        
        collector = VMwareCollector(sources)
        
        assert len(collector.sources) == 1
        assert collector.sources[0].name == "vc1"
    
    @patch('collectors.vmware.SmartConnect')
    def test_validate_connection(self, mock_connect):
        """Test connection validation."""
        from collectors.vmware import VMwareCollector
        
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        sources = [{"name": "vc1", "host": "vc1", "user": "u", "password": "p"}]
        collector = VMwareCollector(sources)
        
        result = collector.validate_connection()
        
        assert result is True
        mock_connect.assert_called_once()


class TestOpenShiftCollector:
    """Tests for OpenShift collector."""
    
    def test_openshift_config_creation(self):
        """Test OpenShift config creation."""
        from collectors.openshift import OpenShiftConfig, OpenShiftCollector
        
        config = OpenShiftConfig(
            name="ocp-prod",
            api_url="https://api.test.com:6443",
            token="fake-token"
        )
        
        assert config.name == "ocp-prod"
        assert config.verify_ssl is True
    
    def test_openshift_collector_init(self):
        """Test OpenShift collector initialization."""
        from collectors.openshift import OpenShiftCollector
        
        sources = [
            {"name": "ocp1", "api_url": "https://api.test.com:6443", "token": "t"}
        ]
        
        collector = OpenShiftCollector(sources)
        
        assert len(collector.sources) == 1


class TestBareMetalCollector:
    """Tests for Bare Metal collector."""
    
    def test_baremetal_config_creation(self):
        """Test BareMetal config creation."""
        from collectors.baremetal import BareMetalConfig, BareMetalCollector
        
        config = BareMetalConfig(
            target="10.0.0.1",
            community="public",
            snmp_version="2c"
        )
        
        assert config.target == "10.0.0.1"
        assert config.snmp_version == "2c"
    
    def test_baremetal_collector_init(self):
        """Test BareMetal collector initialization."""
        from collectors.baremetal import BareMetalCollector
        
        targets = [{"target": "10.0.0.1", "community": "public"}]
        
        collector = BareMetalCollector(targets)
        
        assert len(collector.targets) == 1