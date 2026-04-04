"""Bare Metal Collector using SNMP and SSH."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

import paramiko
from pysnmp.hlapi import *


logger = logging.getLogger(__name__)


@dataclass
class BareMetalConfig:
    """Configuration for Bare Metal collector."""
    target: str
    community: str = 'public'
    snmp_version: str = '2c'
    ssh_enabled: bool = False
    ssh_user: str = ''
    ssh_key_path: str = ''


class BareMetalCollector:
    """Collector for Bare Metal servers via SNMP/SSH."""
    
    def __init__(self, targets: List[Dict]):
        self.targets = [BareMetalConfig(**t) for t in targets]
        
    def validate_connection(self) -> bool:
        """Validate SNMP connectivity to targets."""
        for target in self.targets[:1]:  # Test first target
            try:
                iterator = getCmd(
                    SnmpEngine(),
                    CommunityData(target.community, mpModel=1 if target.snmp_version == '2c' else 0),
                    UdpTransportTarget((target.target, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if errorIndication:
                    logger.error(f"SNMP failed for {target.target}: {errorIndication}")
                    return False
                    
                logger.info(f"SNMP validated for {target.target}")
                return True
                
            except Exception as e:
                logger.error(f"Connection failed for {target.target}: {e}")
                return False
    
    def discover(self) -> List[Dict[str, Any]]:
        """Discover all bare metal servers."""
        all_servers = []
        
        for target in self.targets:
            try:
                server = self._discover_via_snmp(target)
                if server:
                    all_servers.append(server)
            except Exception as e:
                logger.error(f"Discovery failed for {target.target}: {e}")
                
        return all_servers
    
    def _discover_via_snmp(self, target: BareMetalConfig) -> Dict[str, Any]:
        """Discover server via SNMP."""
        server = {
            'hostname': '',
            'ip_address': target.target,
            'mac_address': '',
            'manufacturer': '',
            'model': '',
            'serial_number': '',
            'cpu_cores': 0,
            'memory_gb': 0,
            'disk_gb': 0,
            'os': '',
            'snmp_contact': '',
            'snmp_location': '',
            'status': 'unknown'
        }
        
        # OIDs to query
        oids = {
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'sysName': '1.3.6.1.2.1.1.5.0',
            'sysContact': '1.3.6.1.2.1.1.4.0',
            'sysLocation': '1.3.6.1.2.1.1.6.0',
        }
        
        for name, oid in oids.items():
            try:
                iterator = getCmd(
                    SnmpEngine(),
                    CommunityData(target.community, mpModel=1),
                    UdpTransportTarget((target.target, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
                
                errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
                
                if not errorIndication and varBinds:
                    value = varBinds[0][1]
                    if name == 'sysDescr':
                        server['os'] = str(value)
                    elif name == 'sysName':
                        server['hostname'] = str(value)
                    elif name == 'sysContact':
                        server['snmp_contact'] = str(value)
                    elif name == 'sysLocation':
                        server['snmp_location'] = str(value)
                        
            except Exception as e:
                logger.debug(f"Failed to get {name} for {target.target}: {e}")
        
        # Try to get more details via SSH if enabled
        if target.ssh_enabled and target.ssh_user:
            try:
                ssh_info = self._discover_via_ssh(target)
                server.update(ssh_info)
            except Exception as e:
                logger.warning(f"SSH discovery failed for {target.target}: {e}")
        
        server['status'] = 'online'
        return server
    
    def _discover_via_ssh(self, target: BareMetalConfig) -> Dict[str, Any]:
        """Discover additional details via SSH."""
        info = {}
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if target.ssh_key_path:
                client.connect(
                    hostname=target.target,
                    username=target.ssh_user,
                    key_filename=target.ssh_key_path,
                    timeout=10
                )
            else:
                client.connect(
                    hostname=target.target,
                    username=target.ssh_user,
                    password=os.getenv('SSH_PASSWORD'),
                    timeout=10
                )
            
            # Get hostname
            stdin, stdout, stderr = client.exec_command('hostname')
            info['hostname'] = stdout.read().decode().strip()
            
            # Get CPU cores
            stdin, stdout, stderr = client.exec_command('nproc')
            info['cpu_cores'] = int(stdout.read().decode().strip())
            
            # Get memory in GB
            stdin, stdout, stderr = client.exec_command("free -g | awk '/^Mem:/{print $2}'")
            info['memory_gb'] = int(stdout.read().decode().strip())
            
        finally:
            client.close()
            
        return info