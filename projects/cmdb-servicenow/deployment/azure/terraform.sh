# Azure Terraform - CMDB ServiceNow Discovery

> Déploiement Infrastructure as Code avec Terraform

---

## Fichiers

```
azure/
├── main.tf              # Main configuration
├── variables.tf         # Variables
├── outputs.tf           # Outputs
├── versions.tf          # Provider versions
├── 01-network.tf       # VNet, subnets
├── 02-keyvault.tf       # Key Vault
├── 03-monitor.tf       # Log Analytics
└── 04-aro.tf           # ARO (partial)
```

---

## versions.tf

```terraform
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azapi = {
      source  = "azure/azapi"
    }
  }
}

provider "azurerm" {
  features {}
  
  subscription_id = var.subscription_id
  tenant_id      = var.tenant_id
  client_id      = var.client_id
  client_secret  = var.client_secret
}
```

---

## variables.tf

```terraform
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "canadacentral"
}

variable "service_now_instance" {
  description = "ServiceNow instance name"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

variable "client_id" {
  description = "Service principal client ID"
  type        = string
}

variable "client_secret" {
  description = "Service principal client secret"
  type        = string
  sensitive   = true
}
```

---

## 01-network.tf

```terraform
# Hub VNet
resource "azurerm_virtual_network" "hub" {
  name                = "vnet-hub-${var.environment}"
  location            = azurerm_resource_group.cmdb.location
  resource_group_name = azurerm_resource_group.cmdb.name
  address_space       = ["10.100.0.0/16"]
  
  subnet {
    name           = "AzureFirewallSubnet"
    address_prefix = "10.100.20.0/24"
  }
  
  subnet {
    name           = "BastionSubnet"
    address_prefix = "10.100.30.0/24"
  }
  
  subnet {
    name           = "PrivateEndpointSubnet"
    address_prefix = "10.100.50.0/24"
  }
}

# ARO VNet (Spoke)
resource "azurerm_virtual_network" "aro" {
  name                = "vnet-aro-${var.environment}"
  location            = azurerm_resource_group.cmdb.location
  resource_group_name = azurerm_resource_group.cmdb.name
  address_space       = ["10.101.0.0/16"]
  
  subnet {
    name           = "MasterSubnet"
    address_prefix = "10.101.0.0/24"
  }
  
  subnet {
    name           = "WorkerSubnet"
    address_prefix = "10.101.1.0/24"
  }
}

# VNet Peering
resource "azurerm_virtual_network_peering" "hub_to_aro" {
  name                      = "hub-to-aro"
  virtual_network_name      = azurerm_virtual_network.hub.name
  resource_group_name       = azurerm_resource_group.cmdb.name
  remote_virtual_network_id = azurerm_virtual_network.aro.id
  allow_forwarded_traffic   = true
}

resource "azurerm_virtual_network_peering" "aro_to_hub" {
  name                      = "aro-to-hub"
  virtual_network_name      = azurerm_virtual_network.aro.name
  resource_group_name       = azurerm_resource_group.cmdb.name
  remote_virtual_network_id = azurerm_virtual_network.hub.id
  allow_forwarded_traffic   = true
}
```

---

## 02-keyvault.tf

```terraform
resource "azurerm_key_vault" "cmdb" {
  name                = "kv-cmdb-${var.environment}"
  location            = azurerm_resource_group.cmdb.location
  resource_group_name = azurerm_resource_group.cmdb.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  
  sku_name = "standard"
  
  enable_rbac_authorization = true
  enable_soft_delete       = true
  soft_delete_retention_days = 90
  
  network_acls {
    bypass                     = "AzureServices"
    default_action             = "Allow"
    ip_rules                   = ["10.100.30.0/24"]
  }
}

# Secrets - Note: Use azcli to set actual values
# resource "azurerm_key_vault_secret" "servicenow_user" {
#   name         = "servicenow-username"
#   key_vault_id = azurerm_key_vault.cmdb.id
#   value        = "SET_VALUE_HERE"
# }
```

---

## 03-monitor.tf

```terraform
resource "azurerm_log_analytics_workspace" "cmdb" {
  name                = "la-cmdb-${var.environment}"
  location            = azurerm_resource_group.cmdb.location
  resource_group_name = azurerm_resource_group.cmdb.name
  
  sku          = "PerGB2018"
  retention_in_days = 30
}

resource "azurerm_monitor_action_group" "cmdb" {
  name                = "ag-cmdb-${var.environment}"
  resource_group_name = azurerm_resource_group.cmdb.name
  short_name          = "cmdb"
  
  webhook_receiver {
    name        = "alerts"
    service_uri = "https://webhook.example.com/alerts"
  }
}
```

---

## main.tf

```terraform
# Resource Group
resource "azurerm_resource_group" "cmdb" {
  name     = "rg-cmdb-${var.environment}"
  location = var.location
  
  tags = {
    Environment = var.environment
    Project     = "CMDB-Discovery"
  }
}

# Data
data "azurerm_client_config" "current" {}

# Import existing ARO cluster (example)
# data "azurerm_redhat_openshift_cluster" "aro" {
#   name                = "cmdb-aro-${var.environment}"
#   resource_group_name = "resource-group-containing-aro"
# }
```

---

## outputs.tf

```terraform
output "resource_group_name" {
  value = azurerm_resource_group.cmdb.name
}

output "hub_vnet_id" {
  value = azurerm_virtual_network.hub.id
}

output "aro_vnet_id" {
  value = azurerm_virtual_network.aro.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.cmdb.vault_uri
}

output "log_analytics_workspace" {
  value = azurerm_log_analytics_workspace.cmdb.name
}
```

---

## Déploiement

```bash
# Initialize
terraform init

# Plan
terraform plan -var-file=prod.tfvars

# Apply
terraform apply -var-file=prod.tfvars
```

---

## prod.tfvars

```terraform
environment          = "prod"
location             = "canadacentral"
service_now_instance = "company"
subscription_id      = "your-subscription-id"
tenant_id            = "your-tenant-id"
client_id            = "your-client-id"
client_secret        = "your-client-secret"
```

---

*Terraform configuration pour CMDB ServiceNow Discovery*
*Dernière mise à jour: 2026-04-04*