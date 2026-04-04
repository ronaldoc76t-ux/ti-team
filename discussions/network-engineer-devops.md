# Discussion: Network Engineer ↔ DevOps

## Scénario 1: Besoin de connectivité pour déploiement Kubernetes

**DevOps:**
Je déploie un nouveau cluster K8s. Besoin de:
- Range IPs: 10.50.0.0/16 pour pods
- Load balancer HTTP: 80, 443
- Accès aux nodes depuis CIDR ops: 10.0.1.0/24

**Network Engineer:**
Je config:
- VLAN K8s (VLAN 50), subnet 10.50.0.0/16
- Firewall rules: allow 10.0.1.0/24 → 10.50.0.0/16:80,443
- Je crée aussi une route vers le subnet pods

**DevOps:**
Parfait. Je schedule le déploiement pour demain.

---

## Scénario 2: CI/CD pipeline échoue, network timeout

**DevOps:**
Le runner GitLab ne peut pas pull les images Docker depuis le registry. Timeout connection.

**Network Engineer:**
Tu utilises quel registry?

**DevOps:**
Docker Hub et notre registry interne registry.internal.com.

**Network Engineer:**
Je check. Le registry interne est derrière un VPN. Je ouvre le port 5000 depuis le subnet CI runners.

**DevOps:**
Merci. Je reteste le pipeline.

---

## Scénario 3: Request changement DNS pour nouveau service

**DevOps:**
On lance un nouveau service "api-prod". Je besoin d'un DNS entry:
- api-prod.internal.com → 10.50.2.100

**Network Engineer:**
Je ajoute le record DNS. A-record créé.

**DevOps:**
Je vérifie... ça marche. Thanks!