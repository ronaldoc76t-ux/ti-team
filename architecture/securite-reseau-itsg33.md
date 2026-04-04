# Contraintes de Sécurité Réseau - ITSG-33

> Politique de validation des flux entre zones réseau

---

## 1. Modèle de Zones ITSG-33

### 1.1 Définition des Zones

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │     ZONE DMZ      │
                    │  (Démilitarisée)  │
                    │  Serveurs publics │
                    │  Reverse proxy    │
                    └─────────┬─────────┘
                              │ Flux autorisé: HTTP/HTTPS, DNS
                              │
┌─────────────────────────────┼───────────────────────────────────┐
│                    ZONE ITSG-33                                  │
│  (Applications & Données sensibles)                              │
│  ┌────────────────┐    ┌────────────────┐    ┌────────────────┐  │
│  │  Zone Apps    │    │   Zone Data    │    │   Zone Mgmt   │  │
│  │  Web Apps     │    │   Databases    │    │   Admin       │  │
│  │  API interne  │    │   Backup      │    │   SSH/RDP    │  │
│  └────────────────┘    └────────────────┘    └────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ ZONE INDUSTRIELLE │
                    │    (Purdue)       │
                    │  - OT/ICS         │
                    │  - Controllers    │
                    │  - SCADA          │
                    └───────────────────┘
```

### 1.2 Classification des Zones

| Zone | Données | Niveau Sensibilité | Connectivité |
|------|---------|-------------------|--------------|
| Internet | Publique | None | Entrante |
| DMZ | Semi-publique | Faible | Entrante/Sortante |
| ITSG-33 Apps | Interne | Moyen-Élevé | Entrante/Sortante |
| ITSG-33 Data | Sensible | Élevé | Sortante uniquement |
| Industrielle | Critique | Critique | Isolée |

---

## 2. Règles de Flux Entre Zones

### 2.1 Matrice de Flux Autorisés

| Source \ Destination | DMZ | ITSG-33 Apps | ITSG-33 Data | Industrielle | Internet |
|---------------------|-----|--------------|--------------|--------------|----------|
| **Internet** | ✅ HTTP/HTTPS, DNS | ❌ | ❌ | ❌ | - |
| **DMZ** | - | ✅ App-specific | ❌ | ❌ | ✅ HTTP/HTTPS |
| **ITSG-33 Apps** | ✅ Response | - | ✅ SQL/Data | ❌ | ❌ |
| **ITSG-33 Data** | ❌ | ✅ Read-only | - | ❌ | ❌ |
| **Industrielle** | ❌ | ❌ | ❌ | - | ❌ |

### 2.2 Règles Détaillées

#### 🌐 Internet → DMZ
```
PROTOCOL: TCP
PORTS: 80, 443, 53
SOURCE: ANY
DESTINATION: DMZ servers
INSPECTION: L7 (Threat Prevention)
```

#### 🛡️ DMZ → ITSG-33 Apps
```
PROTOCOL: TCP
PORTS: Application-specific (8080, 8443, etc.)
SOURCE: DMZ reverse proxy
DESTINATION: App servers
INSPECTION: L7, Malware scan
AUTH: Certificate mutual (mTLS)
```

#### 💾 ITSG-33 Apps → ITSG-33 Data
```
PROTOCOL: TCP
PORTS: 5432 (PostgreSQL), 3306 (MySQL), 1433 (MSSQL)
SOURCE: App servers
DESTINATION: Database servers
INSPECTION: L7, SQL injection prevention
AUTH: Service account + IP whitelist
```

#### 🔒 ITSG-33 Data → ITSG-33 Apps (Response)
```
PROTOCOL: TCP
PORTS: Same as source port
SOURCE: Database servers
DESTINATION: App servers
STATE: Stateful (established)
```

#### 🚫 ITSG-33 → Industrielle
```
TOUT FLUX: INTERDIT
EXCEPTION: Documentée case-by-case par Security Architect
```

---

## 3. Contraintes de Sécurité par Zone

### 3.1 DMZ (Zone Démilitarisée)

| Contrainte | Exigence |
|------------|----------|
| **Inspection** | L7 (App layer) obligatoire |
| **Chiffrement** | TLS 1.2+ minimum |
| **Authentification** | Certificat serveur |
| **Logging** | Tous les accès, full logs |
| **Rate limiting** | Enabled, 100 req/s par IP |
| **WAF** | Activé pour services HTTP |

### 3.2 Zone ITSG-33 (Apps & Data)

| Contrainte | Exigence |
|------------|----------|
| **Segmentation** | VLAN distincts par subnet |
| **Inspection** | L7 sur tous les flux inter-zones |
| **Authentification** | LDAP/AD + MFA |
| **Chiffrement** | TLS 1.3 preferred |
| **Backup** | Quotidien, chiffré, hors site |
| **Journalisation** | 90 jours minimum |

### 3.3 Zone Industrielle (Purdue)

| Contrainte | Exigence |
|------------|----------|
| **Air-gapped** | Pas de connexion directe Internet |
| **Physique** | Accès contrôlé |
| **Protocoles** | Modbus, OPC-UA, Profinet uniquement |
| **Monitoring** | Read-only pour monitoring |
| **Patch** | Évaluation préalable, fenêtre maintenance |
| ** Segmentation** | VLAN OT isolé |

---

## 4. Validation des Flux

### 4.1 Processus de Demande de Flux

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Demande   │────►│   Review    │────►│   Approval  │
│   (User)    │     │ (Net Arch)  │     │ (Sec Arch)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Implément. │
                    │ (Net Engineer)│
                    └──────────────┘
```

### 4.2 Critères de Validation

#### ✅ Requête Acceptée Si:
- Justification métier documentée
- Flux nécessaire au fonctionnement
- Alternative plus sécurisée impossible
- Impact sécurité évalué et acceptable
- Approbation Security Architect

#### ❌ Requête Refusée Si:
- Flux inter-zone non justifié
- Niveau sensibilité incompatible
- Violation principe moindre privilège
- Risque non mitigate

### 4.3 Template de Demande

```markdown
## Demande de Flux Réseau

**Demandeur:** [Nom/Équipe]
**Date:** YYYY-MM-DD
**Justification:** [Description du besoin métier]

### Flux Détails

| Champ | Valeur |
|-------|--------|
| Source Zone | |
| Source IP/Host | |
| Destination Zone | |
| Destination IP/Host | |
| Protocol | |
| Port(s) | |
| Direction | |

### Justification Métier

[Pourquoi ce flux est nécessaire]

### Alternatives Evaluées

[Options envisagées et pourquoi refusées]

### Mesures de Mitigation

[Comment réduire le risque]
```

---

## 5. Palo Alto - Règles de Sécurité

### 5.1 Stratégie de Règles

| Règle | Action | Ordre |
|-------|--------|-------|
| Deny All | DROP | Dernier |
| Industrielle → Any | DENY | Avant-dernier |
| ITSG-33 Data → Internet | DENY | Intermédiaire |
| DMZ → ITSG-33 Apps | ALLOW (inspect) | Standard |
| Internet → DMZ | ALLOW (inspect) | Standard |

### 5.2 Configuration Type

```yaml
# Exemple règle firewall
name: "DMZ_TO_ITSG33_APPS"
source_zone: "DMZ"
destination_zone: "ITSG33_APPS"
source_address: "10.100.0.0/24"
destination_address: "10.50.0.0/16"
application: "ssl,http,custom-app"
action: "allow"
profile: "best-practice-threat"
log: "yes"
```

---

## 6. Audit et Conformité

### 6.1 Vérifications Périodiques

| Fréquence | Vérification |
|-----------|--------------|
| Hebdomadaire | Revue logs denies |
| Mensuel | Audit règles firewall |
| Trimestriel | Penetration testing |
| Annuel | Revue ITSG-33 complète |

### 6.2 Indicateurs de Conformité

- ✅ Tous les flux inter-zones documentés
- ✅ Règles " deny all" en place
- ✅ Inspection L7 sur flux critiques
- ✅ Logging de tout le trafic
- ✅ Revue trimestrielle des règles

---

## 7. Synthèse

| Principe | Application |
|----------|-------------|
| **Least Privilege** | only explicitly allowed flows |
| **Defense in Depth** | L7 inspection + segmentation |
| **Zero Trust** | No trust by default, verify always |
| **Auditability** | Full logging all flows |
| **Isolation** | Industrial zone air-gapped |

---

*Document conforme ITSG-33*
*Dernière mise à jour: 2026-04-04*