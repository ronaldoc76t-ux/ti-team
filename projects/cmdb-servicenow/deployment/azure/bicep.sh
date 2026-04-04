# Azure Bicep - CMDB ServiceNow Discovery

> Déploiement Infrastructure as Code avec Azure Bicep

---

## Fichiers

```
azure/
├── main.bicep          # Main template
├── modules/
│   ├── network.bicep   # VNet, subnets
│   ├── aro.bicep       # ARO cluster
│   ├── keyvault.bicep  # Key Vault
│   └── monitor.bicep   # Log Analytics
├── params/
│   └── prod.json       # Parameters
└── deploy.sh           # Deployment script
```

---

## main.bicep

```bicep
// Main Bicep Template - CMDB Discovery Azure Infrastructure
targetScope = 'subscription'

@description('Environment name (prod/staging)')
@allowed(['prod', 'staging'])
param environment string = 'prod'

@description('Location for all resources')
param location string = 'canadacentral'

@description('ServiceNow instance (without service-now.com)')
param serviceNowInstance string

@description('Admin username for VMs')
param adminUsername string

// Resource Group
resource rgCmdb 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-cmdb-${environment}'
  location: location
}

// VNet Hub
module vnetHub './modules/network.bicep' = {
  scope: resourceGroup(rgCmdb.name)
  params: {
    environment: environment
    location: location
    addressSpace: '10.100.0.0/16'
  }
}

// ARO Cluster (requires manual creation via Azure Portal/CLI)
// This module creates the supporting resources
module aroSupport './modules/aro.bicep' = {
  scope: resourceGroup(rgCmdb.name)
  params: {
    environment: environment
    location: location
    vnetId: vnetHub.outputs.vnetId
  }
}

// Key Vault
module keyVault './modules/keyvault.bicep' = {
  scope: resourceGroup(rgCmdb.name)
  params: {
    environment: environment
    location: location
    serviceNowInstance: serviceNowInstance
  }
}

// Monitor
module monitor './modules/monitor.bicep' = {
  scope: resourceGroup(rgCmdb.name)
  params: {
    environment: environment
    location: location
  }
}

// Outputs
output vnetId string = vnetHub.outputs.vnetId
output keyVaultUri string = keyVault.outputs.keyVaultUri
output logAnalyticsWorkspace string = monitor.outputs.logAnalyticsWorkspace
```

---

## modules/network.bicep

```bicep
// Network Module - Hub VNet
param environment string
param location string
param addressSpace string

// Virtual Network
resource vnetHub 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'vnet-hub-${environment}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [addressSpace]
    }
    subnets: [
      {
        name: 'AzureFirewallSubnet'
        properties: {
          addressPrefix: '10.100.20.0/24'
        }
      }
      {
        name: 'BastionSubnet'
        properties: {
          addressPrefix: '10.100.30.0/24'
        }
      }
      {
        name: 'PrivateEndpointSubnet'
        properties: {
          addressPrefix: '10.100.50.0/24'
        }
      }
    ]
  }
}

// Peerings will be added manually or via separate module
// ARO creates its own VNet

output vnetId string = vnetHub.id
output vnetName string = vnetHub.name
```

---

## modules/keyvault.bicep

```bicep
// Key Vault Module
param environment string
param location string
param serviceNowInstance string

resource kv 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: 'kv-cmdb-${environment}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: false
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// Secrets (using template outputs - set actual values separately)
resource secretSnUser 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv.name
  name: 'servicenow-username'
  properties: {
    value: '' // Set via Azure Portal or CLI
    contentType: 'string'
  }
}

resource secretSnPass 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: kv.name
  name: 'servicenow-password'
  properties: {
    value: '' // Set via Azure Portal or CLI
    contentType: 'string'
  }
}

output keyVaultUri string = kv.properties.vaultUri
output keyVaultName string = kv.name
```

---

## modules/monitor.bicep

```bicep
// Monitoring Module - Log Analytics
param environment string
param location string

resource la 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: 'la-cmdb-${environment}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
    }
  }
}

// Diagnostic Settings for ARO (to be added)
resource diag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'cmdb-diagnostics'
  scope: la
  properties: {
    workspaceId: la.id
    logs: [
      {
        category: 'AzureActivityLog'
        enabled: true
      }
      {
        category: 'KubeAPIAudit'
        enabled: true
      }
    ]
  }
}

output logAnalyticsWorkspace string = la.name
output logAnalyticsId string = la.id
```

---

## params/prod.json

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "prod"
    },
    "location": {
      "value": "canadacentral"
    },
    "serviceNowInstance": {
      "value": "company"
    },
    "adminUsername": {
      "value": "cmdbadmin"
    }
  }
}
```

---

## deploy.sh

```bash
#!/bin/bash
# Deploy Azure Infrastructure with Bicep

set -e

ENVIRONMENT=${1:-prod}
LOCATION=canadacentral
SUBSCRIPTION=$(az account show --query id -o tsv)

echo "Deploying CMDB Discovery Infrastructure..."
echo "Environment: $ENVIRONMENT"
echo "Location: $LOCATION"
echo ""

# Login check
az account show > /dev/null 2>&1 || az login

# Set subscription
az account set --subscription "$SUBSCRIPTION"

# Deploy main template
echo "Deploying main template..."
az deployment sub create \
  --name "cmdb-$ENVIRONMENT-deploy" \
  --location "$LOCATION" \
  --template-file azure/main.bicep \
  --parameters azure/params/$ENVIRONMENT.json \
  --parameters environment=$ENVIRONMENT

echo ""
echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Create ARO cluster via Azure Portal or CLI:"
echo "   az aro create \\"
echo "     --resource-group rg-cmdb-$ENVIRONMENT \\"
echo "     --name cmdb-aro-$ENVIRONMENT \\"
echo "     --vnet vnet-hub-$ENVIRONMENT \\"
echo "     --master-subnet 10.100.40.0/24 \\"
echo "     --worker-subnet 10.100.41.0/24"
echo ""
echo "2. Set Key Vault secrets:"
echo "   az keyvault secret set \\"
echo "     --vault-name kv-cmdb-$ENVIRONMENT \\"
echo "     --name servicenow-username \\"
echo "     --value YOUR_USERNAME"
echo ""
echo "3. Deploy CMDB Discovery to ARO"
```

---

## Commandes de Déploiement

```bash
# Déployer l'infrastructure
cd /path/to/cmdb-servicenow
chmod +x azure/deploy.sh
./azure/deploy.sh prod

# Vérifier le déploiement
az group show -n rg-cmdb-prod
az network vnet show -n vnet-hub-prod -g rg-cmdb-prod
az keyvault show -n kv-cmdb-prod -g rg-cmdb-prod
```

---

*Azure Bicep templates pour CMDB ServiceNow Discovery*
*Dernière mise à jour: 2026-04-04*