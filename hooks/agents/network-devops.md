# Hook: network-engineer ↔ devops

> Communication entre Network Engineer et DevOps

---

## Événements

| Event | From → To | Description |
|-------|-----------|-------------|
| `agent.net.deploy` | devops → network-engineer | Demande config réseau pour déploiement |
| `agent.net.config` | network-engineer → devops | Configuration réseau prête |
| `agent.net.monitor` | devops → network-engineer | Demande monitoring réseau |
| `agent.net.alert` | network-engineer → devops | Alerte réseau affectant déploiement |

---

## Exemples d'Utilisation

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Demande config réseau pour déploiement
send_to_agent(
    'devops',
    'network-engineer',
    'Config réseau requise pour app-v2',
    priority=MessagePriority.HIGH,
    context={
        'application': 'app-v2',
        'environment': 'staging',
        'required_ports': [443, 8080],
        'vpc_subnet': '10.0.20.0/24'
    }
)

# Alerte réseau
send_to_agent(
    'network-engineer',
    'devops',
    'Bandwidth critique sur lien prod',
    priority=MessagePriority.URGENT,
    context={
        'alert_type': 'bandwidth',
        'current_usage': '95%',
        'impact': 'latence deployment'
    }
)
```

---

## Use Cases

- **Déploiement**: Config DNS, firewall rules, load balancer
- **Monitoring**: Métriques réseau pour applications
- **Alertes**: Problèmes réseau affectant les services