"""ServiceNow CMDB API Client."""

import logging
import os
from typing import Dict, List, Any, Optional

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException


logger = logging.getLogger(__name__)


class ServiceNowClient:
    """Client for ServiceNow CMDB REST API."""
    
    def __init__(self, instance: str, username: str = None, password: str = None):
        self.instance = instance
        self.username = username or os.getenv('SERVICENOW_USER')
        self.password = password or os.getenv('SERVICENOW_PASS')
        self.base_url = f"https://{instance}.service-now.com/api/now/table"
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def create(self, table: str, data: Dict) -> Optional[str]:
        """Create a record in ServiceNow."""
        url = f"{self.base_url}/{table}"
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            sys_id = result.get('result', {}).get('sys_id')
            logger.info(f"Created record in {table}: {sys_id}")
            return sys_id
            
        except RequestException as e:
            logger.error(f"Failed to create record in {table}: {e}")
            return None
    
    def update(self, table: str, sys_id: str, data: Dict) -> bool:
        """Update a record in ServiceNow."""
        url = f"{self.base_url}/{table}/{sys_id}"
        
        try:
            response = self.session.patch(url, json=data, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Updated record in {table}: {sys_id}")
            return True
            
        except RequestException as e:
            logger.error(f"Failed to update record in {table}: {e}")
            return False
    
    def upsert(self, table: str, unique_key: str, data: Dict) -> Optional[str]:
        """Insert or update a record based on unique key."""
        # First try to find existing record
        existing = self._query(table, f"name={unique_key}")
        
        if existing:
            sys_id = existing[0].get('sys_id')
            self.update(table, sys_id, data)
            return sys_id
        else:
            return self.create(table, data)
    
    def query(self, table: str, filter: str = None, fields: List[str] = None) -> List[Dict]:
        """Query records from ServiceNow."""
        url = f"{self.base_url}/{table}"
        
        params = {}
        if filter:
            params['sysparm_query'] = filter
        if fields:
            params['sysparm_fields'] = ','.join(fields)
            
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get('result', [])
            
        except RequestException as e:
            logger.error(f"Failed to query {table}: {e}")
            return []
    
    def _query(self, table: str, filter: str) -> List[Dict]:
        """Internal query helper."""
        return self.query(table, filter)
    
    def delete(self, table: str, sys_id: str) -> bool:
        """Delete a record from ServiceNow."""
        url = f"{self.base_url}/{table}/{sys_id}"
        
        try:
            response = self.session.delete(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Deleted record from {table}: {sys_id}")
            return True
            
        except RequestException as e:
            logger.error(f"Failed to delete record from {table}: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test connection to ServiceNow."""
        try:
            # Try to query the API version
            response = self.session.get(
                f"https://{self.instance}.service-now.com/api/now/table/cmdb_ci_server",
                params={'sysparm_limit': 1},
                timeout=10
            )
            return response.status_code == 200
            
        except RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False