# Architecture - CMDB ServiceNow Discovery

> Document d'architecture pour l'implantation de la découverte CMDB ServiceNow

---

## 1. Contexte du Projet

### 1.1 Objectif
Implanter un système de découverte automatique des assets TI et synchronisation vers CMDB ServiceNow.

### 1.2 Périmètre
- Découverte : Infra on-premise (VMware, OpenShift, Bare Metal)
- Cible : CMDB ServiceNow
- Fréquence : Quotidienne

### 1.3 Contraintes ITSG-33
- Les données de découverte ne doivent pas quitter les zones autorisées
- Authentification via service account avec least privilege
- Journalisation de toutes les interactions

---

## 2. Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFRA ON-PREMISE                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   vCenter    │    │  OpenShift   │    │  Bare Metal  │              │
│  │   (API)      │    │    (API)     │    │   (Agents)   │              │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
│         │                   │                   │                      │
└─────────┼───────────────────┼───────────────────┼──────────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Discovery Engine │
                    │   (Docker/VM)     │
                    │  - vSphere SDK    │
                    │  - OC Client      │
                    │  - SNMP/SSH       │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐
    │ Transform    │  │   Validate  │  │  Logging  │
    │ (Normalize)  │  │   (Rules)   │  │  (Audit)  │
    └───────────────┘  └─────────────┘  └───────────┘
                              │
                    ┌─────────▼─────────┐
                    │  ServiceNow API  │
                    │   (REST CMDB)     │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   CMDB ServiceNow │
                    │   (Tables: CMDB)   │
                    └───────────────────┘
```

---

## 3. Composants

### 3.1 Discovery Engine

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **vSphere Collector** | Go + govmomi | Découverte VMs, hosts, datastores |
| **OpenShift Collector** | Go + oc client | Découverte pods, services, volumes |
| **Bare Metal Collector** | Python + SNMP/SSH | Découverte serveurs physiques |
| **Normalizer** | Python | Normalisation des données |
| **ServiceNow Connector** | Python + requests | Intégration API REST |

### 3.2 Technologie

| Catégorie | Choix |
|-----------|-------|
| **Langage** | Python 3.11 / Go 1.21 |
| **Orchestration** | Docker / OpenShift |
| **Configuration** | YAML |
| **CI/CD** | GitLab CI / Jenkins |
| **Monitoring** | Prometheus + Grafana |

---

## 4. Zones Réseau - ITSG-33

### 4.1 Flux Réseau

| Source | Destination | Protocole | Port | Justification |
|--------|-------------|-----------|------|---------------|
| Discovery Engine | vCenter | HTTPS | 443 | API vSphere |
| Discovery Engine | OpenShift API | HTTPS | 6443 | API K8s |
| Discovery Engine | Bare Metal | SNMP/SSH | 161/22 | Discovery |
| Discovery Engine | ServiceNow | HTTPS | 443 | REST API |
| Discovery Engine | ITSG-33 Data | - | - | NONE (push only) |

### 4.2 Règles Firewall

- **Zone**: ITSG-33 Apps → ServiceNow Cloud (DMZ)
- **Inspection**: L7
- **Auth**: OAuth / API Key

---

## 5. Modèle de Données

### 5.1 Tables ServiceNow Cible

| Table | Description |
|-------|-------------|
| `cmdb_ci_server` | Serveurs |
| `cmdb_ci_vm` | Machines virtuelles |
| `cmdb_ci_kubernetes_cluster` | Clusters K8s |
| `cmdb_ci_kubernetes_pod` | Pods |
| `cmdb_ci_datastore` | Datastores |

### 5.2 Attributs Standards

```
- name: Nom de l'asset
- ip_address: Adresse IP
- discovery_source: 'auto_cddd' (identifiant source)
- discovery_date: Date de découverte
- classification: Sensibilité ITSG-33
- zone: Zone réseau
```

---

## 6. Sécurité

### 6.1 Authentification

| Système | Méthode |
|---------|---------|
| vCenter | Service Account (read-only) |
| OpenShift | Service Account + RBAC |
| Bare Metal | SNMP v3 / SSH Key |
| ServiceNow | OAuth 2.0 / API Key |

### 6.2 Chiffrement

- **En transit**: TLS 1.3 obligatoire
- **Au repos**: Chiffrement si stockage local (LUKS)

### 6.3 Journalisation

- Toutes les exécutions loguées
- Destination: ELK / Syslog
- Rétention: 90 jours

---

## 7. Haute Disponibilité

### 7.1 Stratégie

| Composant | Disponibilité |
|-----------|---------------|
| Discovery Engine | Active/Passive (2 instances) |
| Config | GitOps (versionné) |
| State | Redis (cache) |

### 7.2 Recovery

- RTO: 4 heures
- RPO: 24 heures (discovery quotidien)

---

## 8. Interfaces Externes

### 8.1 API ServiceNow

```
Endpoint: /api/now/table/{table_name}
Method: POST (create), PATCH (update)
Auth: Basic Auth / OAuth
```

### 8.2 Sources de Découverte

| Source | API/Protocole |
|--------|---------------|
| VMware | vSphere REST API |
| OpenShift | Kubernetes API |
| Bare Metal | SNMP, SSH |

---

## 9. Livrables

| Livrable | Emplacement |
|----------|-------------|
| Architecture | `architecture/` |
| Design | `design/` |
| Code | `implementation/` |
| Scripts | `scripts/` |
| Config | `config/` |
| Tests | `tests/` |
| Déploiement | `deployment/` |

---

*Document généré pour l'équipe TI*
*Dernière mise à jour: 2026-04-04*