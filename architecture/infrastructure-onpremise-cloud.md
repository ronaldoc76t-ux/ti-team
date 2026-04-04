# Architecture Infrastructure

> Document de référence pour l'équipe TI

---

## 1. Hébergement On-Premise

### 1.1 Zones Réseau

| Zone | Modèle | Type données | Protection |
|------|--------|--------------|-------------|
| **Zone Industrielle** | Purdue | OT/Industriel | Isolation complète |
| **Zone ITSG-33** | ITSG-33 | Applications & Données | Conformité ITSG-33 |

### 1.2 Modèle Réseau

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└─────────────────────────────┬───────────────────────────────┘
                              │
                      ┌───────▼───────┐
                      │ Palo Alto     │
                      │ Level 7 (NGFW)│
                      └───────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌────────▼────────┐    ┌──────▼──────┐
│ Zone Indus.   │    │ Zone ITSG-33     │    │   DMZ       │
│ (Purdue)      │    │ (Apps/Data)      │    │             │
│ - OT/ICS      │    │ - Web Apps      │    │ - API ext   │
│ - Controllers │    │ - DB            │    │ - Reverse   │
│ - VLAN:10-19  │    │ - VLAN:50-99    │    │   Proxy     │
└───────────────┘    └────────┬────────┘    └─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ F5 LTM             │
                    │ Load Balancing     │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐
    │ OpenShift     │  │ OpenVirt    │  │ APIM      │
    │ (Containers)  │  │ (VM)        │  │ Azure     │
    │               │  │             │  │ Self-hosted│
    └───────────────┘  └─────────────┘  └───────────┘
```

### 1.3 Composants

#### 🔴 Firewall
- **Modèle**: Palo Alto Networks (NGFW)
- **Fonctions**: Inspection niveau 7 (Application Layer)
- **Deployment**: Cluster actif/passif ou actif/actif

#### ⚡ Load Balancer
- **Modèle**: F5 Big-IP LTM
- **Fonctions**: Load balancing L4-L7, SSL termination, WAF

#### 🐳 Container Platform
- **Solution**: Red Hat OpenShift (Self-hosted)
- **Usage**: Applications conteneurisées

#### 💻 Virtualisation
- **Solution**: oVirt / OpenVirt
- **Usage**: Machines virtuelles

#### 🌐 API Management
- **Solution**: Azure API Management (Self-hosted)
- **Deployment**: On-premise / OpenShift

---

## 2. Hébergement Cloud Azure

### 2.1 Stratégie

| Principe | Application |
|----------|-------------|
| **Priorité** | ARO (Azure Red Hat OpenShift) |
| **IaaS** | Minimum (préférer PaaS/Saas) |
| **Connectivité** | Express Route |
| **Topologie** | Hub & Spoke |

### 2.2 Architecture Cloud

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERNET                                │
└─────────────────────────────┬───────────────────────────────┘
                              │
                      ┌───────▼───────┐
                      │ Palo Alto     │
                      │ Level 7       │
                      │ (Cloud NGFW)  │
                      └───────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────────┐  ┌──▼────────────┐  ┌────▼─────┐
    │ Hub Virtual       │  │ Spoke 1       │  │ Spoke 2  │
    │ Network           │  │ (ARO)         │  │ ( workloads)│
    │ - Gateway        │  │ - OpenShift   │  │           │
    │ - Firewall       │  │ - APIM        │  │           │
    │ - ExpressRoute  │  │ - Apps        │  │           │
    └─────────────────┘  └───────────────┘  └───────────┘
              │
    Express Route
    (Private)
              │
┌─────────────▼─────────────┐
│    On-Premise Network     │
│    (connected via ER)    │
└───────────────────────────┘
```

### 2.3 Composants

#### ☁️ Azure Red Hat OpenShift (ARO)
- **Priorité**: Premier choix d'hébergement
- **Usage**: Applications conteneurisées en production

#### 🔒 Palo Alto (Cloud)
- **Modèle**: VM-Series ou Azure Firewall Premium
- **Fonctions**: Inspection L7, threat prevention

#### 🔗 Express Route
- **Type**: Private peering
- **Bande passante**: À dimensionner selon besoins
- **Redondance**: Double circuit (multi-site)

#### 🏢 Hub & Spoke
- **Hub**: Réseau central (connectivité, firewall, services communs)
- **Spoke**: Réseaux workload (ARO, applications)

#### 🌐 APIM Self-hosted
- **Solution**: Azure API Management (self-hosted)
- **Deployment**: Dans ARO (Kubernetes)
- **Usage**: Gestion des API internes et externes

### 2.4 Principes de Design

1. **Zéro IaaS** : Privilégier PaaS/SaaS quand possible
2. **ARO first** : OpenShift comme plateforme applicative par défaut
3. **Micro-services** : Architecture distribuée
4. **Private endpoints** : Pas d'exposition publique inutile
5. **CIS/CSP** : Conformité Azure Security Center

---

## 3. Connectivité Inter-Sites

```
On-Premise                       Cloud Azure
┌──────────────┐              ┌──────────────┐
│   Zone ITSG  │◄───Express───│    Hub      │
│   (Data)     │    Route     │  (Azure)    │
└──────────────┘              └──────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │ Spoke ARO    │
                              │ (Workloads)  │
                              └──────────────┘
```

---

## 4. Synthèse Composants

| Catégorie | On-Premise | Cloud Azure |
|-----------|------------|-------------|
| **Firewall** | Palo Alto (L7) | Palo Alto (L7) |
| **Load Balancer** | F5 LTM | Azure Load Balancer / F5 |
| **Container** | OpenShift | ARO |
| **VM** | oVirt | Azure VMs (minimal) |
| **APIM** | Azure APIM self-hosted | Azure APIM self-hosted |
| **Connectivité** | - | Express Route |

---

## 5. Standards ITSG-33

L'infrastructure on-premise respecte le modèle **ITSG-33** pour la protection des données classifiées sensibles.

### Points clés :
- Séparation réseau stricte (zones)
- Inspection L7 sur tous les flux
- Journalisation et monitoring
- Chiffrement en transit
- Accès authentifié

---

*Document généré à partir des specs équipe TI*
*Dernière mise à jour: 2026-04-04*