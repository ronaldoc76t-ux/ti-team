# Processus de Livraison

> Processus standard pour la mise en production des applications

---

## Types de Produits

| Type | Description |
|------|-------------|
| **Développement Maison** | Applications internes, custom, développé par l'équipe TI |
| **COTS** | Commercial Off-The-Shelf, solutions tierces acquises |

---

## 1. Développement Maison

### 1.1 Pipeline de Livraison

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Archit.  │───►│  Build   │───►│   Test   │───►│ Staging │───►│ Review  │───►│Production│───►│Post-Release│
│ (Design) │    │ (CI/CD)  │    │ (UT/IT)  │    │ (Pre-prod)│  │ (Sign-off)│  │          │    │           │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 1.2 Étapes de Livraison

#### Étape 1: Architecture & Design
- **Responsable**: Solution Architect / Technical Lead
- **Critères**:
  - Architecture documentée
  - Spécifications techniques validées
  - Design compatible avec l'infrastructure (ITSG-33, zones réseau)
  - Review sécurité réalisée
  - Impact sur les flux réseau documenté

#### Étape 2: Build & Compilation
  - Tests unitaires passent (>80% coverage)
  - Analyse statique (SonarQube) sans Blocker/Critical
  - Secrets non exposés dans le code

#### Étape 3: Tests
- **Responsable**: QA / Développeur
- **Critères**:
  - Tests d'intégration passent
  - Tests fonctionnels validés
  - Tests de performance (si applicable)
  - Tests de sécurité (SAST/DAST)
  - Smoke tests post-déploiement staging

#### Étape 4: Staging (Pré-production)
- **Responsable**: DevOps
- **Critères**:
  - Déploiement automatique via CI/CD
  - Configuration production (sans données réelles)
  - Monitoring activé
  - Logs fonctionnels
  - Accès limité équipe QA/Dev

#### Étape 5: Revue et Sign-off
- **Responsable**: Technical Lead / Product Owner
- **Critères**:
  - Documentation mise à jour
  - Release notes préparées
  - Rollback plan documenté
  - Tests UAT validés
  - ✅ Sign-off obtenu

#### Étape 6: Production
- **Responsable**: DevOps / SysAdmin
- **Critères**:
  - Fenêtre de maintenance respectée
  - Déploiement blue/green ou canary
  - Monitoring en place
  - Runbook disponible
  - Équipe support notifiée

#### Étape 7: Post-production
- **Responsable**: DevOps / QA
- **Critères**:
  - Vérification bon fonctionnement (D+1)
  - Métriques performantes
  - Incidents documentés
  - Retrospective réalisée

---

### 1.3 Checklist de Livraison

```markdown
## Checklist Release - [Nom Application]

### Architecture
- [ ] Architecture documentée
- [ ] Spécifications validées
- [ ] Review sécurité OK
- [ ] Impact réseau documenté (zones ITSG-33)

### Build
- [ ] Compilation OK
- [ ] Tests unitaires > 80%
- [ ] SonarQube: pas de Blocker/Critical
- [ ] Pas de secrets dans le code

### Test
- [ ] Tests d'intégration OK
- [ ] Tests fonctionnels OK
- [ ] Tests performance OK (si applicable)
- [ ] Tests sécurité OK

### Staging
- [ ] Déploiement automatique OK
- [ ] Smoke tests OK
- [ ] Monitoring actif

### Revue
- [ ] Documentation à jour
- [ ] Release notes préparées
- [ ] Plan de rollback prêt
- [ ] Sign-off: [Nom] - [Date]

### Production
- [ ] Fenêtre maintenance respectée
- [ ] Déploiement réussi
- [ ] Monitoring vérifié

### Post-Release
- [ ] Vérification D+1 OK
- [ ] Pas d'incident critique
```

---

## 2. Produits COTS

### 2.1 Pipeline d'Acquisition

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Archit.  │───►│  Analyse │───►│  Achat   │───►│  Test    │───►│ Staging  │───►│Production│───►│Post-Release│
│ (Design) │    │  Besoin  │    │ (Vendor) │    │ (POC)    │    │ (UAT)    │    │          │    │           │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### 2.2 Étapes de Livraison

#### Étape 1: Architecture & Design
- **Responsable**: Solution Architect / Cloud Architect
- **Critères**:
  - Architecture d'intégration documentée
  - Compatibilité zones réseau (ITSG-33)
  - Requirements network/firewall identifiés
  - Review sécurité réalisée
  - Plan de connectivité validé

#### Étape 2: Analyse du Besoin
- **Responsable**: Product Owner / Architecture
  - alternatives évaluées (build vs buy)
  -fit avec l'infrastructure existante
  - Coût total de possession (TCO) estimé

#### Étape 3: Acquisition (Vendor)
- **Responsable**: Achats / ITAM
- **Critères**:
  - Contrat signé (SLA, support)
  - License conforme aux besoins
  - Documentation acquise
  - Accès vendor établi

#### Étape 4: Test / POC
- **Responsable**: QA / Intégrateur
- **Critères**:
  - POC fonctionnel
  - Tests de performance
  - Tests de sécurité
  - Intégration avec systèmes existants
  - Validation des fonctionnalités clés

#### Étape 5: Staging (UAT)
- **Responsable**: QA / Métier
- **Critères**:
  - Déploiement en environnement UAT
  - Tests utilisateurs validés
  - Formation utilisateurs
  - Processus support documenté
  - Intégration monitoring

#### Étape 6: Production
- **Responsable**: SysAdmin / Intégrateur
- **Critères**:
  - Fenêtre de maintenance respectée
  - Déploiement réussi
  - Configuration sécurisée
  - Monitoring et alerting actifs
  - Accès support vendor vérifié

#### Étape 7: Post-production
- **Responsable**: SysAdmin / Support
- **Critères**:
  - Vérification bon fonctionnement (D+1)
  - Support Levels activés
  - Métriques de performance collectées
  - Documentation utilisateur distribuée

---

### 2.3 Checklist COTS

```markdown
## Checklist COTS - [Nom Produit]

### Architecture
- [ ] Architecture d'intégration documentée
- [ ] Compatibilité zones réseau OK
- [ ] Requirements firewall/network identifiés
- [ ] Review sécurité OK
- [ ] Plan de connectivité validé

### Analyse
- [ ] Besoin métier documenté
- [ ] Alternatives évaluées
- [ ]fit infrastructure vérifié
- [ ] TCO estimé

### Acquisition
- [ ] Contrat signé
- [ ] License OK
- [ ] Documentation reçue
- [ ] Accès vendor OK

### Test/POC
- [ ] POC fonctionnel
- [ ] Tests performance OK
- [ ] Tests sécurité OK
- [ ] Intégration systèmes OK

### Staging/UAT
- [ ] Déploiement UAT OK
- [ ] Tests UAT validés
- [ ] Formation réalisée
- [ ] Processus support OK

### Production
- [ ] Déploiement réussi
- [ ] Configuration sécurisée
- [ ] Monitoring actif
- [ ] Support vendor vérifié

### Post-Release
- [ ] Vérification D+1 OK
- [ ] Support Levels actifs
```

---

## 3. Rollback

### 3.1 Stratégie Commune

| Type | Stratégie |
|------|-----------|
| **Maison** | Blue/Green ou Canary deployment |
| **COTS** | Snapshot/vm backup avant upgrade |

### 3.2 Procédure

1. Détecter l'incident
2. Évaluer la sévérité
3. Si critique → **Rollback immédiat**
4.Notifier l'équipe
5. Analyser la cause racine
6. Documenter et planifier correction

---

## 4. Rôles et Responsabilités

| Rôle | Responsabilité |
|------|----------------|
| **Développeur** | Code, tests, documentation |
| **DevOps** | CI/CD, déploiement, monitoring |
| **QA** | Tests, validation, UAT |
| **Technical Lead** | Sign-off technique |
| **Product Owner** | Sign-off fonctionnel |
| **SysAdmin** | Production, rollback |
| **Sécurité** | Review sécurité |

---

## 5. Standards Communs

### Sécurité (Les deux types)
- ✅ Scan vulnérabilités (CVEs)
- ✅ Configuration hardenée
- ✅ Accès least privilege
- ✅ Logging activé
- ✅ Monitoring actif

### Documentation
- README technique
- Guide d'installation
- Runbook exploitation
- Procédure de support

---

*Document applicable à toute l'équipe TI*
*Dernière mise à jour: 2026-04-04*