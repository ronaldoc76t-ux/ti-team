import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import yaml
import schedule
import time

from collectors.vmware import VMwareCollector
from collectors.openshift import OpenShiftCollector
from collectors.baremetal import BareMetalCollector
from normalizer.transform import Normalizer
from servicenow.client import ServiceNowClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CMDBDiscovery:
    """Main entry point for CMDB discovery."""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.normalizer = Normalizer()
        self.servicenow = ServiceNowClient(
            instance=self.config['servicenow']['instance'],
            username=os.getenv('SERVICENOW_USER'),
            password=os.getenv('SERVICENOW_PASS')
        )
        self.collectors = self._init_collectors()
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = os.getenv('CONFIG_PATH', 'config/config.yaml')
            
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_collectors(self) -> Dict[str, Any]:
        """Initialize all collectors based on config."""
        collectors = {}
        
        if self.config['collectors']['vmware']['enabled']:
            collectors['vmware'] = VMwareCollector(
                self.config['collectors']['vmware']['sources']
            )
            
        if self.config['collectors']['openshift']['enabled']:
            collectors['openshift'] = OpenShiftCollector(
                self.config['collectors']['openshift']['sources']
            )
            
        if self.config['collectors']['baremetal']['enabled']:
            collectors['baremetal'] = BareMetalCollector(
                self.config['collectors']['baremetal']['targets']
            )
            
        return collectors
    
    def run_discovery(self) -> Dict[str, Any]:
        """Run full discovery cycle."""
        start_time = datetime.utcnow()
        logger.info("Starting CMDB discovery cycle")
        
        results = {
            'start_time': start_time.isoformat(),
            'sources': {},
            'errors': []
        }
        
        for source_name, collector in self.collectors.items():
            try:
                logger.info(f"Running discovery for {source_name}")
                
                if not collector.validate_connection():
                    logger.warning(f"Connection validation failed for {source_name}")
                    results['errors'].append(f"{source_name}: connection failed")
                    continue
                    
                discovered = collector.discover()
                normalized = self.normalizer.transform(source_name, discovered)
                
                results['sources'][source_name] = {
                    'discovered': len(discovered),
                    'normalized': len(normalized)
                }
                
                for record in normalized:
                    self._upsert_cmdb_record(record)
                    
                logger.info(f"{source_name}: {len(discovered)} discovered, {len(normalized)} normalized")
                
            except Exception as e:
                logger.error(f"Error discovering {source_name}: {e}")
                results['errors'].append(f"{source_name}: {str(e)}")
        
        results['end_time'] = datetime.utcnow().isoformat()
        logger.info(f"Discovery cycle complete. Errors: {len(results['errors'])}")
        
        return results
    
    def _upsert_cmdb_record(self, record: Dict) -> bool:
        """Insert or update CMDB record."""
        table = record.get('_table', 'cmdb_ci_server')
        
        try:
            result = self.servicenow.upsert(
                table=table,
                unique_key=record.get('name'),
                data=record
            )
            return result is not None
        except Exception as e:
            logger.error(f"Failed to upsert record {record.get('name')}: {e}")
            return False
    
    def run_scheduled(self):
        """Run discovery and handle scheduling."""
        while True:
            self.run_discovery()
            logger.info("Next run in 24 hours")
            time.sleep(86400)  # 24 hours


def main():
    """Main entry point."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    discovery = CMDBDiscovery(config_path)
    
    # Check if running in scheduled mode
    if os.getenv('SCHEDULED_MODE', 'false').lower() == 'true':
        discovery.run_scheduled()
    else:
        discovery.run_discovery()


if __name__ == '__main__':
    main()