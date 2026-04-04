# Discussion: Network Architect ↔ Security Architect

## Scénario 1: Review architecture réseau

**Security Architect:**
Je review le design réseau pour le nouveau projet. Question: Pourquoi pas de segmentation DMZ pour les services exposés?

**Network Architect:**
Bien spotted. J'ajoute une DMZ entre Internet et LAN:
- DMZ: 10.100.0.0/24
- Web server va là
- Only necessary ports from WAN to DMZ

**Security Architect:**
Parfait. Je propose aussi:
- WAF devant les web services
- Rate limiting sur le firewall

**Network Architect:**
Agreed. Je intégre dans le design final.

---

## Scénario 2: Audit security réseau

**Security Architect:**
L'audit a identifié que le VLAN Mgmt (VLAN 5) est accessible depuis le VLAN Users. Non conforme.

**Network Architect:**
Je crée un ACL:
```
access-list 101 deny ip 10.5.0.0/24 10.10.0.0/16
access-list 101 permit ip any any
```
Applied sur le switch core.

**Security Architect:**
Parfait. Je schedule un re-audit pour valider.