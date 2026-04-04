# Design - CMDB ServiceNow Discovery

> Document de design technique

---

## 1. Décisions de Design

### 1.1 Choix Technologiques

| Choix | Justification |
|-------|---------------|
| **Python 3.11** | Langage principal pour les collecteurs et normalizer |
| **govmomi** | SDK Go official pour VMware vSphere |
| **kubernetes-client Python** | Client K8s officiel pour OpenShift |
| **pysnmp** | Bibliothèque robuste pour SNMP |
| **requests** | Client HTTP pour API ServiceNow |
| **YAML config** | Configuration centralisée, lisible |

### 1.2 Architecture

| Principe | Application |
|----------|-------------|
| **Modularité** | Chaque collecteur est un module indépendant |
| **Stateless** | Pas d'état local, tout en mémoire ou Redis |
| **Extensible** | Ajout de nouveaux collecteurs via interface commune |
| **Retry** | Retry automatique avec exponential backoff |

---

## 2. Modèle de Données

### 2.1 Schema Découverte VMware

```json
{
  "vm": {
    "name": "string",
    "uuid": "uuid",
    "ip_address": "ipv4",
    "mac_address": "mac",
    "cpu": "integer",
    "memory_mb": "integer",
    "disk_gb": "integer",
    "os": "string",
    "esxi_host": "string",
    "datastore": "string",
    "status": "poweredOn|poweredOff|suspended",
    "tags": ["string"],
    "zone": "ITSG-33"
  }
}
```

### 2.2 Schema Découverte OpenShift

```json
{
  "pod": {
    "name": "string",
    "namespace": "string",
    "pod_ip": "ipv4",
    "node": "string",
    "containers": [
      {
        "name": "string",
        "image": "string",
        "ports": ["integer"]
      }
    ],
    "labels": {"key": "value"},
    "status": "Running|Pending|Failed",
    "creation_timestamp": "iso8601"
  },
  "service": {
    "name": "string",
    "namespace": "string",
    "cluster_ip": "ipv4",
    "type": "ClusterIP|LoadBalancer|NodePort",
    "ports": [{"port": "integer", "protocol": "TCP|UDP"}]
  }
}
```

### 2.3 Schema Bare Metal

```json
{
  "server": {
    "hostname": "string",
    "ip_address": "ipv4",
    "mac_address": "mac",
    "manufacturer": "string",
    "model": "string",
    "serial_number": "string",
    "cpu_cores": "integer",
    "memory_gb": "integer",
    "disk_gb": "integer",
    "os": "string",
    "snmp_contact": "string",
    "snmp_location": "string",
    "status": "online|offline|warning"
  }
}
```

### 2.4 Schema Sortie ServiceNow

```json
{
  "cmdb_ci_server": {
    "name": "string",
    "ip_address": "ipv4",
    "mac_address": "mac",
    "discovery_source": "auto_cmdb",
    "discovery_date": "iso8601",
    "manufacturer": "string",
    "model_number": "string",
    "serial_number": "string",
    "cpu_core_count": "integer",
    "ram_capacity": "integer",
    "disk_capacity": "integer",
    "operational_status": "operational|offline",
    "zone": "string"
  },
  "cmdb_ci_vm": {
    "name": "string",
    "ip_address": "ipv4",
    "vm_uuid": "uuid",
    "discovery_source": "auto_cmdb",
    "discovery_date": "iso8601",
    "cpus": "integer",
    "memory": "integer",
    "disk_space": "integer",
    "guest_os": "string",
    "esxi_host": "string",
    "datacenter": "string"
  }
}
```

---

## 3. Flux de Données

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   vCenter   │────►│              │     │              │
│   (API)     │     │              │     │              │
└──────────────┘     │              │     │              │
                     │   Discovery  │────►│ Normalizer  │
┌──────────────┐     │   Engine     │     │   (Transform)│
│  OpenShift  │────►│              │     │              │
│   (API)     │     │              │     └──────┬───────┘
└──────────────┘     │              │            │
                     │              │     ┌──────▼───────┐
┌──────────────┐     │              │     │              │
│  Bare Metal │────►│              │     │ ServiceNow   │
│  (SNMP)     │     │              │     │   API         │
└──────────────┘     └──────────────┘     │   (REST)     │
                                           └──────┬───────┘
                                                  │
                                          ┌──────▼───────┐
                                          │   CMDB       │
                                          │ ServiceNow   │
                                          └──────────────┘
```

---

## 4. Composants

### 4.1 Collector Interface

```python
class BaseCollector(ABC):
    @abstractmethod
    def discover(self) -> List[Dict]:
        """Return list of discovered assets"""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connectivity to source"""
        pass
```

### 4.2 VMware Collector

| Méthode | Description |
|---------|-------------|
| `discoverVMs()` | Liste toutes les VMs avec propriétés |
| `discoverHosts()` | Liste les ESXi hosts |
| `discoverDatastores()` | Liste les datastores |

### 4.3 OpenShift Collector

| Méthode | Description |
|---------|-------------|
| `discoverPods()` | Liste tous les pods |
| `discoverServices()` | Liste les services |
| `discoverNodes()` | Liste les nodes |

### 4.4 Bare Metal Collector

| Méthode | Description |
|---------|-------------|
| `discoverViaSNMP()` | Découverte SNMP v2c/v3 |
| `discoverViaSSH()` | Découverte SSH (fallback) |

### 4.5 Normalizer

```python
class Normalizer:
    def transform_vmware(data) -> CMDBRecord
    def transform_openshift(data) -> CMDBRecord
    def transform_baremetal(data) -> CMDBRecord
    def validate(record) -> bool
```

### 4.6 ServiceNow Client

```python
class ServiceNowClient:
    def create(table, data) -> str  # sys_id
    def update(table, sys_id, data) -> bool
    def upsert(table, unique_key, data) -> bool
    def query(table, filter) -> List[Dict]
```

---

## 5. API Contracts

### 5.1 Collecteur → Normalizer

```json
// Input
POST /normalize
Content-Type: application/json

{
  "source": "vmware|openshift|baremetal",
  "data": [...]
}

// Output
200 OK
{
  "normalized": [...],
  "errors": [...]
}
```

### 5.2 Normalizer → ServiceNow

```json
// Input
POST /api/now/table/cmdb_ci_server
Content-Type: application/json
Authorization: Basic base64(user:pass)

{
  "name": "server-001",
  "ip_address": "10.1.1.1",
  "discovery_source": "auto_cmdb",
  "discovery_date": "2026-04-04T12:00:00Z"
}
```

### 5.3 Configuration API

```yaml
collectors:
  vmware:
    enabled: true
    schedule: "0 2 * * *"  # 2am daily
    sources:
      - name: "vcenter-prod"
        host: "vcenter.internal.com"
        
  openshift:
    enabled: true
    schedule: "0 3 * * *"
    sources:
      - name: "ocp-prod"
        api_url: "https://api.ocp.internal.com:6443"
        
  baremetal:
    enabled: true
    schedule: "0 4 * * *"
    targets:
      - "10.0.0.0/24"
```

---

## 6. Gestion des Erreurs

| Scénario | Stratégie |
|----------|-----------|
| Connexion source échoue | Retry 3x, puis skip avec log |
| Auth ServiceNow échoue | Alert, pas de mise à jour |
| Données invalides | Log + skip, continue |
| Timeout | Retry exponential backoff |

---

*Document de design pour l'équipe TI*
*Dernière mise à jour: 2026-04-04*