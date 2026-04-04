# Azure Configuration - CMDB ServiceNow Discovery

> Configuration Azure pour l'hébergement Cloud du projet

---

## Architecture Azure

```
┌─────────────────────────────────────────────────────────────┐
│                      Azure Hub VNet                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Azure Firewall / APIM                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │                │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐       │
│  │ ARO Cluster │   │  Jump Host  │   │   Private    │       │
│  │   (Prod)    │   │   (Bastion) │   │    Endpoint  │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
         │                                  │
         │        Express Route             │
         └──────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         │   On-Premise Network (Purdue) │
         └───────────────────────────────┘
```

---

## Services Azure Utilisés

| Service | Usage | SKU Minimum |
|---------|-------|-------------|
| **ARO** | OpenShift cluster | Standard |
| **Azure Firewall** | Sécurisation egress | Standard |
| **Private Endpoint** | ServiceNow API | Standard |
| **Key Vault** | Secrets management | Standard |
| **Log Analytics** | Monitoring | Per GB |
| **Express Route** | Connectivité hybride | 1 Gbps |

---

## Réseau - Hub & Spoke

```yaml
# Azure Network Configuration
hub_vnet:
  address_space: "10.100.0.0/16"
  location: "canadacentral"
  
  subnets:
    # Management
    management: "10.100.10.0/24"
    
    # Azure Firewall
    azure_firewall: "10.100.20.0/24"
    
    # Jump hosts / Bastion
    bastion: "10.100.30.0/24"
    
    # ARO cluster (spoke)
    aro_pod: "10.100.40.0/24"
    aro_service: "10.100.41.0/24"
    aro_ingress: "10.100.42.0/24"

spoke_vnet_aro:
  address_space: "10.101.0.0/16"
  peer_to_hub: true
  
  subnets:
    # Master nodes
    master: "10.101.0.0/24"
    
    # Worker nodes
    worker: "10.101.1.0/24"
    
    # Private link
    privatelink: "10.101.2.0/24"

# Express Route
express_route:
  provider: "Microsoft"
  peering_location: "Toronto"
  bandwidth: "1Gbps"
  circuit_sku: "Standard"
```

---

## Configuration ARO

```yaml
# Azure Red Hat OpenShift
aro:
  # Cluster configuration
  cluster_name: "cmdb-aro-prod"
  resource_group: "rg-cmdb-prod"
  location: "canadacentral"
  
  # Network
  vnet: "vnet-aro-prod"
  vnet_cidr: "10.101.0.0/16"
  pod_cidr: "10.128.0.0/14"
  service_cidr: "10.128.0.0/16"
  
  # Master nodes
  master:
    count: 3
    vm_size: "Standard_D8s_v3"
    
  # Worker nodes
  worker:
    count: 3
    vm_size: "Standard_D4s_v3"
    autoscale:
      min: 2
      max: 5
  
  # API Server
  api_server:
    visibility: "Private"
    authorized_ip_ranges:
      - "10.100.30.0/24"  # Bastion
  
  # Ingress
  ingress:
    visibility: "Private"
    load_balancer: "Internal"
```

---

## Private Endpoint - ServiceNow

```yaml
# ServiceNow Private Endpoint
private_endpoint:
  enabled: true
  
  # Resource to connect
  resource_type: "web"
  resource: "company.service-now.com"
  
  # Subnet
  subnet: "10.100.50.0/24"
  
  # DNS
  dns:
    # Use Azure Private DNS Zone
    use_private_zone: true
    zone_name: "service-now.com"
    
    # DNS records
    a_record: "company.service-now.com"
    
    # Custom DNS (on-prem resolution)
    on_prem_dns:
      - "10.0.0.53"  # DNS server in Purdue network
```

---

## Secrets - Key Vault

```yaml
# Azure Key Vault
key_vault:
  name: "kv-cmdb-prod"
  resource_group: "rg-cmdb-prod"
  location: "canadacentral"
  
  # Secrets
  secrets:
    # ServiceNow
    - name: "servicenow-username"
      secret_name: "cmdb-servicenow-user"
    - name: "servicenow-password"
      secret_name: "cmdb-servicenow-pass"
    
    # VMware
    - name: "vcenter-username"
      secret_name: "vcenter-user"
    - name: "vcenter-password"
      secret_name: "vcenter-pass"
    
    # OpenShift
    - name: "openshift-token"
      secret_name: "openshift-token"
    
    # Database (if needed)
    - name: "db-connection-string"
      secret_name: "db-conn-string"
  
  # Access policy
  access_policy:
    # ARO Service Account
    - object_id: "<aro-service-principal>"
      permissions:
        keys: ["get", "list"]
        secrets: ["get", "list"]
        
    # Jenkins / CI/CD
    - object_id: "<jenkins-sp>"
      permissions:
        secrets: ["get", "list", "set"]
  
  # Network access
  network:
    bypass: "AzureServices"
    default_action: "Deny"
    ip_rules:
      - "10.100.30.0/24"  # Bastion
```

---

## Monitoring - Azure Monitor

```yaml
# Azure Monitor Configuration
monitoring:
  # Log Analytics
  log_analytics:
    workspace: "la-cmdb-prod"
    resource_group: "rg-cmdb-prod"
    retention_days: 30
    
  # Metrics
  metrics:
    enabled: true
    retention_days: 90
    
  # Alerts
  alerts:
    - name: "Discovery-Failed"
      condition: "metric > 0"
      severity: "1"  # Critical
      frequency: "PT1H"
      
    - name: "High-CPU-ARO"
      condition: "metric > 80"
      severity: "2"  # Error
      frequency: "PT5M"
      
    - name: "Pod-Restarting"
      condition: "count > 5"
      severity: "3"  # Warning
      frequency: "PT15M"

  # Application Insights
  app_insights:
    enabled: false  # Optional - for deeper APM
```

---

## Déploiement - ARM Template

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "aroClusterName": {
      "type": "string",
      "defaultValue": "cmdb-aro-prod"
    },
    "location": {
      "type": "string",
      "defaultValue": "canadacentral"
    }
  },
  "resources": [
    {
      "type": "Microsoft.ContainerService/openShiftClusters",
      "apiVersion": "2023-09-01",
      "name": "[parameters('aroClusterName')]",
      "location": "[parameters('location')]",
      "properties": {
        "resourceGroup": "rg-cmdb-prod",
        "masterPoolProfile": {
          "count": 3,
          "vmSize": "Standard_D8s_v3"
        },
        "workerPoolProfile": {
          "count": 3,
          "vmSize": "Standard_D4s_v3"
        }
      }
    }
  ]
}
```

---

## Variables d'Environnement - Azure

```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=
AZURE_TENANT_ID=
AZURE_RESOURCE_GROUP=rg-cmdb-prod
AZURE_LOCATION=canadacentral

# ARO Configuration
ARO_API_SERVER=https://api.cmdb-aro-prod.canadacentral.aroapp.io:6443
ARO_TOKEN=${AZURE_ARO_TOKEN}

# Private Endpoint
SERVICENOW_INSTANCE=company.service-now.com
SERVICENOW_PRIVATE_ENDPOINT=company.privatelink.service-now.com

# Key Vault
KEY_VAULT_NAME=kv-cmdb-prod
```

---

## Checklist Déploiement Azure

- [ ] Créer VNet Hub (10.100.0.0/16)
- [ ] Déployer Azure Firewall
- [ ] Configurer Express Route vers on-prem
- [ ] Créer VNet Spoke ARO (10.101.0.0/16)
- [ ] Déployer ARO cluster
- [ ] Configurer Private Endpoint pour ServiceNow
- [ ] Configurer Key Vault
- [ ] Configurer Log Analytics
- [ ] Déployer CMDB Discovery sur ARO
- [ ] Tester connectivité vers ServiceNow
- [ ] Configurer alerts monitoring

---

*Configuration Azure pour CMDB ServiceNow Discovery*
*Dernière mise à jour: 2026-04-04*