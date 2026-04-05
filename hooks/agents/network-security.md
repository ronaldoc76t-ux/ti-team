# Hook: network-engineer ↔ security

> Communication entre Network Engineer et Security

---

## Événements

| Event | From → To | Description |
|-------|-----------|-------------|
| `agent.net.sec` | network-engineer → security | Demande review sécurité réseau |
| `agent.sec.net` | security → network-engineer | Alerte sécurité réseau |
| `agent.firewall.req` | security → network-engineer | Demande création regla firewall |
| `agent.audit.net` | security → network-engineer | Demande audit réseau |

---

## Exemples d'Utilisation

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Demande review sécurité
send_to_agent(
    'network-engineer',
    'security',
    'Review sécurité nouveau VLAN',
    priority=MessagePriority.NORMAL,
    context={
        'vlan': 'VLAN-DB',
        'subnet': '10.0.50.0/24',
        'reason': 'nouvelle base de données'
    }
)

# Alerte firewall
send_to_agent(
    'security',
    'network-engineer',
    'Bloquer trafic suspect détecté',
    priority=MessagePriority.URGENT,
    context={
        'alert_type': 'intrusion_attempt',
        'source_ip': '192.168.1.100',
        'action': 'block'
    }
)
```

---

## Use Cases

- **Review sécurité**: Nouveaux segments réseau
- **Firewall rules**: Création/blocking de règles
- **Audit**: Review périodique des configs réseau