# Hooks - Webhook Handlers for TI Team Agents

> Webhooks pour déclencher les agents TI lors d'événements externes

---

## Structure

```
hooks/
├── README.md           # Ce fichier
├── webhook-handler.py  # Script handler principal
├── events/             # Définitions des événements
│   ├── gitlab.yaml
│   ├── jira.yaml
│   ├── servicenow.yaml
│   └── monitoring.yaml
├── templates/          # Templates de payloads
│   ├── discovery-trigger.yaml
│   └── incident-trigger.yaml
└── config.yaml         # Configuration des webhooks
```

---

## Événements Supportés

| Event Source | Events |
|-------------|--------|
| **GitLab** | push, merge_request, tag, issue |
| **Jira** | issue_created, issue_updated, transition |
| **ServiceNow** | incident_created, change_approved, cmdb_updated |
| **Monitoring** | alert_fired, alert_resolved |

---

## Configuration

```yaml
# config.yaml
webhook:
  host: "0.0.0.0"
  port: 8080
  endpoint: "/webhook"
  
  # Authentication
  auth:
    type: "bearer"  # ou "basic", "hmac"
    token: "${WEBHOOK_SECRET}"
    
  # Event routing
  routing:
    - event: "git.push"
      agents: ["devops"]
      priority: 1
      
    - event: "jira.issue_created"
      agents: ["technical-lead"]
      priority: 2
      
    - event: "servicenow.incident"
      agents: ["sysadmin", "network-engineer"]
      priority: 1
      
    - event: "monitoring.alert"
      agents: ["security"]
      priority: 1
```

---

## Webhook Handler

```python
#!/usr/bin/env python3
"""Webhook Handler pour TI Team."""

import os
import json
import hmac
import hashlib
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookHandler(BaseHTTPRequestHandler):
    """Handler pour les webhooks entrants."""
    
    def do_POST(self):
        """Handle POST requests."""
        # Read payload
        content_length = int(self.headers.get('Content-Length', 0))
        payload = self.rfile.read(content_length)
        
        # Verify auth
        if not self.verify_auth(payload):
            self.send_error(401, "Unauthorized")
            return
            
        # Parse event
        event_type = self.headers.get('X-Gitlab-Event') or \
                     self.headers.get('X-Jira-Event') or \
                     self.headers.get('X-ServiceNow-Event') or \
                     'unknown'
                     
        # Process event
        try:
            data = json.loads(payload)
            self.route_event(event_type, data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "accepted"}')
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            self.send_error(500, str(e))
    
    def verify_auth(self, payload):
        """Verify authentication."""
        # Simple HMAC verification
        secret = os.getenv('WEBHOOK_SECRET', '')
        if not secret:
            return True  # No secret configured
            
        signature = self.headers.get('X-Signature', '')
        if signature:
            expected = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected)
        return True
    
    def route_event(self, event_type, data):
        """Route event to appropriate agents."""
        logger.info(f"Routing event: {event_type}")
        # Log event for agent polling
        with open('/tmp/webhook-events.json', 'a') as f:
            json.dump({
                'event': event_type,
                'data': data
            }, f)
            f.write('\n')


def main():
    """Main entry point."""
    port = int(os.getenv('WEBHOOK_PORT', 8080))
    server = HTTPServer(('', port), WebhookHandler)
    logger.info(f"Webhook server listening on port {port}")
    server.serve_forever()


if __name__ == '__main__':
    main()
```

---

## Exemples d'Événements

### GitLab Push

```json
{
  "object_kind": "push",
  "event_name": "push",
  "ref": "refs/heads/main",
  "user_username": "developer",
  "project": {
    "path_with_namespace": "ti-team/infrastructure"
  },
  "commits": [
    {
      "id": "abc123",
      "message": "feat: update firewall rules",
      "author": {"name": "Dev"}
    }
  ]
}
```

### ServiceNow Incident

```json
{
  "event": "incident_created",
  "number": "INC001234",
  "short_description": "Production server down",
  "impact": 1,
  "urgency": 1,
  "assigned_to": "sysadmin",
  "cmdb_ci": "server-prod-01"
}
```

### Monitoring Alert

```json
{
  "event": "alert_fired",
  "alertname": "HighCPU",
  "severity": "critical",
  "instance": "prod-server-01",
  "value": "95",
  "timestamp": "2026-04-04T22:00:00Z"
}
```

---

## Intégration avec les Agents

Les agents poll `/tmp/webhook-events.json` pour obtenir les événements:

```python
def check_webhooks():
    """Check for new webhook events."""
    events_file = '/tmp/webhook-events.json'
    if os.path.exists(events_file):
        with open(events_file) as f:
            return [json.loads(line) for line in f]
    return []
```

---

*Hooks pour TI Team Agents*
*Dernière mise à jour: 2026-04-04*