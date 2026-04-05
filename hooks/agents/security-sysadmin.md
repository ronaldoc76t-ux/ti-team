# Hook: security ↔ sysadmin

> Communication entre Security et Sysadmin

---

## Événements

| Event | From → To | Description |
|-------|-----------|-------------|
| `agent.sec.sys` | security → sysadmin | Demande action sécurité |
| `agent.sys.sec` | sysadmin → security | Rapport sécurité |
| `agent.patch.req` | security → sysadmin | Demande patch sécurité |
| `agent.access.req` | sysadmin → security | Demande accès révisé |

---

## Exemples d'Utilisation

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Demande patch
send_to_agent(
    'security',
    'sysadmin',
    'Appliquer patch CVE-2026-0001',
    priority=MessagePriority.URGENT,
    context={
        'cve': 'CVE-2026-0001',
        'severity': 'critical',
        'deadline': '24h'
    }
)

# Rapport sécurité
send_to_agent(
    'sysadmin',
    'security',
    'Rapport hebdomadaire sécurité',
    priority=MessagePriority.NORMAL,
    context={
        'report_type': 'weekly',
        'updates_applied': 5,
        'vulnerabilities_found': 2,
        'resolved': 2
    }
)
```

---

## Use Cases

- **Patch management**: Application de correctifs
- **Vulnerability management**: Rapports et actions
- **Access review**: Révision des accès utilisateurs