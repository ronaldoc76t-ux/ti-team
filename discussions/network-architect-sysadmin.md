# Discussion: Network Architect ↔ SysAdmin

## Scénario 1: Déploiement nouveau serveurrequiert réseau

**SysAdmin:**
J'ai besoin d'un nouveau serveur DB en production. Requirements:
- IP fixe: 10.20.30.45
- Accès internet pour updates
- Ouvertures firewall: port 5432 (PostgreSQL) depuis subnet app

**Network Architect:**
Je config le VLAN DB_VLAN (VLAN 20), subnet 10.20.30.0/24. Je Dok:
- Route vers App subnet 10.10.0.0/16
- Firewall rules: allow 10.10.0.0/16 → 10.20.30.45:5432

**SysAdmin:**
Parfait. Je prévois l'install pour demain 9h.

---

## Scénario 2: Monitoring réseau indisponible

**SysAdmin:**
Je n'ai plus de metrics réseau sur Grafana. Le datasource Prometheus semble ok mais pas de données network.

**Network Architect:**
Tu as vérifié le SNMP exporter sur les switches? Le community string a peut-être changé suite au rotate de credentials.

**SysAdmin:**
Bien vu. Je check le snmpd.conf et restart le service.

**Network Architect:**
Tiens-moi au courant. Si besoin, on recalculera les dashboards une fois résolu.

---

## Scénario 3: Demande d'Accès VPN

**SysAdmin:**
Un développeur a besoin d'accès VPN pour travailler depuis chez lui. C'est un nouveau recruit, account créé.

**Network Architect:**
Je crée l'accès VPN tomorrow. Tu as son laptop MAC address pour le cert client?

**SysAdmin:**
Je te l'envoie par Slack. C'est pour l'accès full-tunnel ou split?

**Network Architect:**
Split-tunnel. Il a besoin que du réseau interne, internet direct.