"""VMware Collector using govmomi SDK."""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect


logger = logging.getLogger(__name__)


@dataclass
class VMwareConfig:
    """Configuration for VMware collector."""
    name: str
    host: str
    user: str
    password: str
    port: int = 443


class VMwareCollector:
    """Collector for VMware vSphere."""
    
    def __init__(self, sources: List[Dict]):
        self.sources = [VMwareConfig(**s) for s in sources]
        
    def validate_connection(self) -> bool:
        """Validate connection to vCenter."""
        for source in self.sources:
            try:
                conn = SmartConnect(
                    host=source.host,
                    user=source.user,
                    pwd=source.password,
                    port=source.port
                )
                Disconnect(conn)
                logger.info(f"Connection validated for {source.name}")
                return True
            except Exception as e:
                logger.error(f"Connection failed for {source.name}: {e}")
                return False
    
    def discover(self) -> List[Dict[str, Any]]:
        """Discover all VMs from vCenter."""
        all_vms = []
        
        for source in self.sources:
            try:
                vms = self._discover_from_source(source)
                all_vms.extend(vms)
            except Exception as e:
                logger.error(f"Discovery failed for {source.name}: {e}")
                
        return all_vms
    
    def _discover_from_source(self, source: VMwareConfig) -> List[Dict[str, Any]]:
        """Discover VMs from a single vCenter."""
        conn = SmartConnect(
            host=source.host,
            user=source.user,
            pwd=source.password,
            port=source.port
        )
        
        try:
            content = conn.content
            view_manager = content.viewManager
            container_view = view_manager.CreateContainerView(
                content.rootFolder,
                [vim.VirtualMachine],
                True
            )
            
            vms = []
            for vm in container_view.view:
                vm_data = self._extract_vm_info(vm)
                vm_data['source'] = source.name
                vms.append(vm_data)
                
            return vms
            
        finally:
            Disconnect(conn)
    
    def _extract_vm_info(self, vm: vim.VirtualMachine) -> Dict[str, Any]:
        """Extract relevant info from VM object."""
        config = vm.config
        summary = vm.summary
        
        # Get IP address
        ip_address = summary.guest.ipAddress or ''
        
        # Get MAC address
        mac_address = ''
        if config and config.hardware:
            for net in config.hardware.device:
                if isinstance(net, vim.vm.VirtualEthernetCard):
                    mac_address = net.macAddress
                    break
        
        # Get CPU and Memory
        cpu = config.hardware.numCPU if config else 0
        memory_mb = config.hardware.memoryMB if config else 0
        
        # Get Disk
        disk_gb = 0
        if config and config.hardware:
            for disk in config.hardware.device:
                if isinstance(disk, vim.vm.VirtualDisk):
                    disk_gb += int(disk.capacityInKB) / 1024 / 1024
        
        # Get OS
        os = summary.guest.guestFullName or ''
        
        # Get ESXi host
        esxi_host = ''
        if vm.runtime.host:
            esxi_host = vm.runtime.host.name
            
        return {
            'name': vm.name,
            'uuid': vm.uuid,
            'ip_address': ip_address,
            'mac_address': mac_address,
            'cpu': cpu,
            'memory_mb': memory_mb,
            'disk_gb': int(disk_gb),
            'os': os,
            'esxi_host': esxi_host,
            'status': str(vm.runtime.powerState),
            'tags': [],
            'zone': 'ITSG-33'
        }