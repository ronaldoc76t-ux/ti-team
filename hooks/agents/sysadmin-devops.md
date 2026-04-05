# Hook: sysadmin ↔ devops

> Communication entre Sysadmin et DevOps

---

## Événements

| Event | From → To | Description |
|-------|-----------|-------------|
| `agent.deploy.req` | devops → sysadmin | Demande déploiement |
| `agent.deploy.resp` | sysadmin → devops | Réponse déploiement |
| `agent.maintenance.req` | devops → sysadmin | Demande maintenance |
| `agent.backup.req` | devops → sysadmin | Demande backup |

---

## Exemples d'Utilisation

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Demande déploiement
send_to_agent(
    'devops',
    'sysadmin',
    'Déployer app-v2 sur prod',
    priority=MessagePriority.HIGH,
    context={
        'application': 'app-v2',
        'environment': 'prod',
        'rollback_plan': 'git revert'
    }
)

# Réponse
send_to_agent(
    'sysadmin',
    'devops',
    'Déploiement terminé avec succès',
    priority=MessagePriority.NORMAL,
    context={
        'application': 'app-v2',
        'status': 'success',
        'duration': '5m'
    }
)
```

---

## Use Cases

- **Déploiement**: DevOps demande à Sysadmin de déployer une app
- **Maintenance**: Fenêtre de maintenance requise
- **Backup**: Demande de backup avant déploiement critique