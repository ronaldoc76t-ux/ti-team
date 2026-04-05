# Inter-Agent Communication Hooks

> Hooks pour la communication entre agents TI-TEAM

---

## Structure

```
hooks/
├── agents/                  # Communication inter-agents
│   ├── README.md           # Ce fichier
│   ├── messenger.py        # Module de messaging
│   ├── events.yaml         # Définition des événements agents
│   └── inbox/              # Boîte de réception par agent
│       ├── sysadmin/
│       ├── network-engineer/
│       ├── security/
│       ├── devops/
│       └── technical-lead/
```

---

## Événements Inter-Agents

| From → To | Event | Description |
|-----------|-------|-------------|
| sysadmin → network-engineer | `agent.net.req` | Demande vérification réseau |
| network-engineer → sysadmin | `agent.sys.req` | Demande restart service |
| security → any | `agent.sec.alert` | Alerte sécurité |
| any → security | `agent.sec.info` | Information pour security |
| devops → sysadmin | `agent.deploy.req` | Demande déploiement |
| network-engineer ↔ security | `agent.net.sec` | Coordonnation sécurité réseau |
| technical-lead → any | `agent.arch.req` | Demande architecture |

---

## Messenger Module

```python
#!/usr/bin/env python3
"""Messenger pour communication inter-agents."""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from enum import Enum


class Agent(Enum):
    """Agents TI-Team."""
    SYSADMIN = "sysadmin"
    NETWORK_ENGINEER = "network-engineer"
    SECURITY = "security"
    DEVOPS = "devops"
    TECHNICAL_LEAD = "technical-lead"
    NETWORK_ARCHITECT = "network-architect"
    INTEGRATEUR = "integrateur"


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class InterAgentMessenger:
    """Messenger pour communication entre agents."""
    
    BASE_DIR = Path(__file__).parent / 'inbox'
    
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.inbox_dir = self.BASE_DIR / agent_name
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        
    def send(self, to_agent, message, priority=MessagePriority.NORMAL, 
             context=None):
        """Envoyer un message à un agent."""
        msg = {
            'id': str(uuid.uuid4()),
            'from': self.agent_name,
            'to': to_agent,
            'message': message,
            'priority': priority.name,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'read': False
        }
        
        # Save to recipient's inbox
        inbox = self.BASE_DIR / to_agent
        inbox.mkdir(parents=True, exist_ok=True)
        
        msg_file = inbox / f"{msg['id']}.json"
        with open(msg_file, 'w') as f:
            json.dump(msg, f, indent=2)
            
        print(f"Message sent to {to_agent}: {message}")
        return msg['id']
    
    def receive(self, unread_only=True):
        """Recevoir les messages."""
        messages = []
        
        for msg_file in self.inbox_dir.glob('*.json'):
            with open(msg_file) as f:
                msg = json.load(f)
                
            if unread_only and msg.get('read'):
                continue
                
            messages.append(msg)
            
        return sorted(messages, key=lambda m: (
            -MessagePriority[m['priority']].value,
            m['timestamp']
        ))
    
    def mark_read(self, message_id):
        """Marquer un message comme lu."""
        msg_file = self.inbox_dir / f"{message_id}.json"
        if msg_file.exists():
            with open(msg_file) as f:
                msg = json.load(f)
            msg['read'] = True
            msg['read_at'] = datetime.utcnow().isoformat() + 'Z'
            with open(msg_file, 'w') as f:
                json.dump(msg, f, indent=2)
    
    def broadcast(self, message, priority=MessagePriority.NORMAL):
        """Broadcast à tous les agents."""
        for agent in Agent:
            if agent.value != self.agent_name:
                self.send(agent.value, message, priority)


# Convenience functions
def send_to_agent(from_agent, to_agent, message, **kwargs):
    """Envoyer un message."""
    messenger = InterAgentMessenger(from_agent)
    return messenger.send(to_agent, message, **kwargs)


def check_inbox(agent_name):
    """Vérifier la boîte de réception."""
    messenger = InterAgentMessenger(agent_name)
    return messenger.receive()
```

---

## Events YAML

```yaml
# events.yaml - Définition des événements inter-agents
events:
  # Demande réseau → sysadmin
  - name: "agent.net.req"
    description: "Network engineer demande action sysadmin"
    from: "network-engineer"
    to: "sysadmin"
    priority: "HIGH"
    fields:
      - task
      - target
      - reason
      
  # Demande sysadmin → network
  - name: "agent.sys.req"
    description: "Sysadmin demande vérification réseau"
    from: "sysadmin"
    to: "network-engineer"
    priority: "NORMAL"
    fields:
      - check_type
      - target
      
  # Alerte sécurité
  - name: "agent.sec.alert"
    description: "Alerte sécurité urgente"
    from: "security"
    to: "*"  # broadcast
    priority: "URGENT"
    fields:
      - severity
      - description
      - affected_systems
      
  # Demande déploiement
  - name: "agent.deploy.req"
    description: "Demande déploiement"
    from: "devops"
    to: "sysadmin"
    priority: "HIGH"
    fields:
      - application
      - environment
      - rollback_plan
      
  # Demande architecture
  - name: "agent.arch.req"
    description: "Demande review architecture"
    from: "technical-lead"
    to: "network-architect"
    priority: "NORMAL"
    fields:
      - project
      - review_type
      
  # Demande coordination
  - name: "agent.coord.req"
    description: "Demande coordination entre agents"
    from: "integrateur"
    to: "*"
    priority: "NORMAL"
    fields:
      - task
      - required_agents
```

---

## Exemples d'Utilisation

### Sysadmin → Network Engineer

```python
from hooks.agents.messenger import send_to_agent, MessagePriority

# Demander vérification réseau
send_to_agent(
    'sysadmin',
    'network-engineer',
    'Vérifier connectivité vers server-prod-01',
    priority=MessagePriority.HIGH,
    context={
        'target': '10.0.10.5',
        'port': 443,
        'reason': 'Service inaccessible'
    }
)
```

### Security Broadcast

```python
# Alerte sécurité à tous les agents
send_to_agent(
    'security',
    'sysadmin',  # Will broadcast to all
    'Vulnérabilité critique détectée - mise à jour requise',
    priority=MessagePriority.URGENT,
    context={
        'cve': 'CVE-2026-0001',
        'severity': 'critical',
        'affected': ['nginx', 'apache'],
        'deadline': '2026-04-05T12:00:00Z'
    }
)
```

### Check Inbox (dans un agent)

```python
from hooks.agents.messenger import check_inbox

# Dans l'agent sysadmin
messages = check_inbox('sysadmin')
for msg in messages:
    print(f"From: {msg['from']}")
    print(f"Message: {msg['message']}")
    print(f"Priority: {msg['priority']}")
```

---

## Webhook Integration

Les messages peuvent être déclenchés via webhooks:

```bash
# Via curl
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Type: agent" \
  -d '{
    "event": "agent.net.req",
    "from": "sysadmin",
    "to": "network-engineer",
    "message": "Check VPN connectivity",
    "context": {"target": "vpn-gateway"}
  }'
```

---

## Scheduler Integration

Les jobs peuvent envoyer des messages:

```yaml
# Dans jobs.yaml
- name: "network-alert-check"
  type: "interval"
  interval_minutes: 5
  agents: ["network-engineer"]
  action:
    type: "check"
    on_alert:
      type: "notify"
      to: "sysadmin"
      message: "Network alert detected"
```

---

*Hooks pour communication inter-agents TI-Team*
*Dernière mise à jour: 2026-04-04*