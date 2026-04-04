"""OpenShift Collector using kubernetes-client Python."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from kubernetes import client
from kubernetes.client.rest import ApiException


logger = logging.getLogger(__name__)


@dataclass
class OpenShiftConfig:
    """Configuration for OpenShift collector."""
    name: str
    api_url: str
    token: str
    verify_ssl: bool = True


class OpenShiftCollector:
    """Collector for OpenShift/Kubernetes."""
    
    def __init__(self, sources: List[Dict]):
        self.sources = [OpenShiftConfig(**s) for s in sources]
        
    def validate_connection(self) -> bool:
        """Validate connection to OpenShift API."""
        for source in self.sources:
            try:
                api = self._create_core_api(source)
                api.list_namespace()
                logger.info(f"Connection validated for {source.name}")
                return True
            except Exception as e:
                logger.error(f"Connection failed for {source.name}: {e}")
                return False
    
    def discover(self) -> List[Dict[str, Any]]:
        """Discover pods and services from all clusters."""
        all_assets = []
        
        for source in self.sources:
            try:
                assets = self._discover_from_source(source)
                all_assets.extend(assets)
            except Exception as e:
                logger.error(f"Discovery failed for {source.name}: {e}")
                
        return all_assets
    
    def _create_core_api(self, source: OpenShiftConfig):
        """Create Kubernetes API client."""
        configuration = client.Configuration()
        configuration.host = source.api_url
        configuration.api_key['authorization'] = f'Bearer {source.token}'
        configuration.verify_ssl = source.verify_ssl
        
        return client.CoreV1Api(client.ApiClient(configuration))
    
    def _discover_from_source(self, source: OpenShiftConfig) -> List[Dict[str, Any]]:
        """Discover from a single OpenShift cluster."""
        api = self._create_core_api(source)
        assets = []
        
        # Discover Pods
        try:
            pods = api.list_pod_for_all_namespaces()
            for pod in pods.items:
                assets.append(self._extract_pod_info(pod, source.name))
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            
        # Discover Services
        try:
            services = api.list_service_for_all_namespaces()
            for svc in services.items:
                assets.append(self._extract_service_info(svc, source.name))
        except ApiException as e:
            logger.error(f"Failed to list services: {e}")
            
        return assets
    
    def _extract_pod_info(self, pod, source_name: str) -> Dict[str, Any]:
        """Extract pod information."""
        containers = []
        for c in pod.spec.containers:
            containers.append({
                'name': c.name,
                'image': c.image,
                'ports': [p.containerPort for p in (c.ports or [])]
            })
        
        return {
            'type': 'pod',
            'name': pod.metadata.name,
            'namespace': pod.metadata.namespace,
            'pod_ip': pod.status.pod_ip or '',
            'node': pod.spec.node_name or '',
            'containers': containers,
            'labels': pod.metadata.labels or {},
            'status': pod.status.phase,
            'creation_timestamp': pod.metadata.creation_timestamp.isoformat() if pod.metadata.creation_timestamp else '',
            'source': source_name
        }
    
    def _extract_service_info(self, svc, source_name: str) -> Dict[str, Any]:
        """Extract service information."""
        ports = []
        for p in (svc.spec.ports or []):
            ports.append({
                'port': p.port,
                'protocol': p.protocol or 'TCP'
            })
        
        return {
            'type': 'service',
            'name': svc.metadata.name,
            'namespace': svc.metadata.namespace,
            'cluster_ip': svc.spec.cluster_ip or '',
            'type': svc.spec.type or 'ClusterIP',
            'ports': ports,
            'labels': svc.metadata.labels or {},
            'source': source_name
        }