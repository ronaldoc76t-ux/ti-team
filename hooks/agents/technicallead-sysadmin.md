# Hook: technical-lead ↔ sysadmin

> Communication entre Technical Lead et Sysadmin

---

## Événements

| Event | From → To | Description |
|-------|-----------|-------------|
| `agent.tl.sys` | technical-lead → sysadmin | Demande technique |
| `agent.sys.tl` | sysadmin → technical-lead | Rapport/Status |
| `agent.deploy.approve` | technical-lead → sysadmin | Approbation déploiement |
| `agent.maintenance.plan` | technical-lead → sysadmin | Plan de maintenance |

---

## Exemples d'Utilisation

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Approbation déploiement
send_to_agent(
    'technical-lead',
    'sysadmin',
    'Approuver déploiement prod v2.1',
    priority=MessagePriority.HIGH,
    context={
        'application': 'app-v2.1',
        'environment': 'prod',
        'approved_by': 'John',
        'notes': 'Tests ok, go for prod'
    }
)

# Rapport status
send_to_agent(
    'sysadmin',
    'technical-lead',
    'Status infrastructure hebdomadaire',
    priority=MessagePriority.NORMAL,
    context={
        'report_type': 'weekly',
        'uptime': '99.9%',
        'incidents': 2,
        'capacity': '75%'
    }
)
```

---

## Use Cases

- **Déploiement**: Approbation avant production
- **Maintenance**: Planification de fenêtres
- **Reporting**: Statuts et rapports techniques