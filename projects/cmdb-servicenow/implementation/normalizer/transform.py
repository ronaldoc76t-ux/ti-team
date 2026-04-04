"""Normalizer - Transform discovery data to ServiceNow CMDB format."""

import logging
from typing import List, Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


# Mapping from discovery source to CMDB table
TABLE_MAPPING = {
    'vmware': 'cmdb_ci_vm',
    'openshift': 'cmdb_ci_kubernetes_pod',
    'baremetal': 'cmdb_ci_server'
}


class Normalizer:
    """Normalize discovery data to ServiceNow CMDB format."""
    
    def __init__(self):
        self.discovery_date = datetime.utcnow().isoformat() + 'Z'
        
    def transform(self, source: str, data: List[Dict]) -> List[Dict]:
        """Transform discovery data based on source."""
        if source == 'vmware':
            return [self._transform_vmware(d) for d in data]
        elif source == 'openshift':
            return [self._transform_openshift(d) for d in data]
        elif source == 'baremetal':
            return [self._transform_baremetal(d) for d in data]
        else:
            logger.warning(f"Unknown source: {source}")
            return []
    
    def _transform_vmware(self, vm: Dict) -> Dict:
        """Transform VMware VM to CMDB format."""
        return {
            '_table': 'cmdb_ci_vm',
            'name': vm.get('name', ''),
            'ip_address': vm.get('ip_address', ''),
            'vm_uuid': vm.get('uuid', ''),
            'discovery_source': 'auto_cmdb',
            'discovery_date': self.discovery_date,
            'cpus': vm.get('cpu', 0),
            'memory': vm.get('memory_mb', 0) // 1024,  # Convert to GB
            'disk_space': vm.get('disk_gb', 0),
            'guest_os': vm.get('os', ''),
            'esxi_host': vm.get('esxi_host', ''),
            'datacenter': vm.get('datacenter', ''),
            'operational_status': 'operational' if vm.get('status') == 'poweredOn' else 'offline',
            'zone': vm.get('zone', 'ITSG-33')
        }
    
    def _transform_openshift(self, asset: Dict) -> Dict:
        """Transform OpenShift asset to CMDB format."""
        if asset.get('type') == 'pod':
            return self._transform_openshift_pod(asset)
        elif asset.get('type') == 'service':
            return self._transform_openshift_service(asset)
        return asset
    
    def _transform_openshift_pod(self, pod: Dict) -> Dict:
        """Transform OpenShift pod to CMDB format."""
        return {
            '_table': 'cmdb_ci_kubernetes_pod',
            'name': f"{pod.get('namespace', '')}/{pod.get('name', '')}",
            'ip_address': pod.get('pod_ip', ''),
            'discovery_source': 'auto_cmdb',
            'discovery_date': self.discovery_date,
            'namespace': pod.get('namespace', ''),
            'node': pod.get('node', ''),
            'status': pod.get('status', ''),
            'labels': str(pod.get('labels', {})),
            'zone': 'ITSG-33'
        }
    
    def _transform_openshift_service(self, svc: Dict) -> Dict:
        """Transform OpenShift service to CMDB format."""
        return {
            '_table': 'cmdb_ci_kubernetes_service',
            'name': f"{svc.get('namespace', '')}/{svc.get('name', '')}",
            'ip_address': svc.get('cluster_ip', ''),
            'discovery_source': 'auto_cmdb',
            'discovery_date': self.discovery_date,
            'namespace': svc.get('namespace', ''),
            'service_type': svc.get('type', 'ClusterIP'),
            'labels': str(svc.get('labels', {})),
            'zone': 'ITSG-33'
        }
    
    def _transform_baremetal(self, server: Dict) -> Dict:
        """Transform Bare Metal server to CMDB format."""
        return {
            '_table': 'cmdb_ci_server',
            'name': server.get('hostname', server.get('ip_address', '')),
            'ip_address': server.get('ip_address', ''),
            'mac_address': server.get('mac_address', ''),
            'discovery_source': 'auto_cmdb',
            'discovery_date': self.discovery_date,
            'manufacturer': server.get('manufacturer', ''),
            'model_number': server.get('model', ''),
            'serial_number': server.get('serial_number', ''),
            'cpu_core_count': server.get('cpu_cores', 0),
            'ram_capacity': server.get('memory_gb', 0),
            'disk_capacity': server.get('disk_gb', 0),
            'operational_status': server.get('status', 'unknown'),
            'os': server.get('os', ''),
            'zone': 'ITSG-33'
        }
    
    def validate(self, record: Dict) -> bool:
        """Validate that record has required fields."""
        required = ['name', 'ip_address', 'discovery_source']
        
        for field in required:
            if field not in record or not record[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        return True