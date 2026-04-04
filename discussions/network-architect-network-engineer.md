# Discussion: Network Architect ↔ Network Engineer

## Scénario 1: Conception d'un nouveau segment réseau

**Network Architect:**
J'ai finalisé le design pour le nouveau segment VLAN10_DOCK. Voici les spécifications:
- VLAN ID: 10
- Subnet: 10.10.10.0/24
- Passerelle: 10.10.10.1
- DHCP: Range 10.10.10.100-200
- Firewall: Regles entrantesallow HTTP/HTTPS vers serveur local

Peux-tu valider la faisabilité technique et prepared la configuration?

**Network Engineer:**
Reçu. Je valide:
- @Cisco3750: VLAN 10 créé, name VLAN10_DOCK
- @dhcpd: Range configuré (10.10.10.100-200)
- @firewall: Rules ajoutées pour 80/443

Question: Tu veux que j'applique maintenant ou on schedule window maintenance?

**Network Architect:**
Applique maintenant. Je dok la configuration dans le change request #CR-2026-0042 pour audit.

---

## Scénario 2: Problème de performance réseau

**Network Engineer:**
J'ai un problème intermittent sur le link uplink vers le firewall. Latence spike à 200ms Randomement. Logs montrent packetloss 2-5%.

**Network Architect:**
Tu as vérifié l'interface fiber SFP? Quel est le % d'erreur sur le port?

**Network Engineer:**
Gi1/0/1 - Errors: 1,234 CRC, 89 frame. Ça sent le problème physique.

**Network Architect:**
Probablement SFP défectueux ou câbles fiber sales. Schedule remplacement pendant window. Je Dok change request pour audit post-mortem.

---

## Scénario 3: Demande de nouveau VPN site-à-site

**Network Architect:**
Besion d'un VPN IPSec vers nouveau partenaire Commercial. Requirements:
- Chiffrement: AES-256
- Auth: Certificats X.509
- Lifetime: 8h
- Peer: 203.0.113.50

**Network Engineer:**
Reçu. Je prepare:
- crypto map configuration
- ISAKMP policy
- Tunnel interface

Deadline?

**Network Architect:**
EOD demain. Je send request à Security pour approval firewall rules.