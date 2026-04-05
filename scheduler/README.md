# Scheduler - Ordonnanceur pour Agents TI

> Planification des tâches récurrentes et événements pour les agents

---

## Structure

```
scheduler/
├── README.md           # Ce fichier
├── scheduler.py        # Moteur d'ordonnancement
├── jobs.yaml           # Définition des jobs
├── triggers/           # Déclencheurs
│   ├── cron.yaml
│   ├── interval.yaml
│   └── dependency.yaml
└── state/              # État des jobs
    └── state.json
```

---

## Types de Jobs

| Type | Description | Exemple |
|------|-------------|---------|
| **cron** | Planification cron standard | Discovery quotidien 2am |
| **interval** | Intervalle fixe | Health check toutes les 5 min |
| **dependency** | Déclenché par un autre job | Post-deployment validation |
| **event** | Déclenché par webhook | Incident créé |

---

## Configuration des Jobs

```yaml
# jobs.yaml
jobs:
  # Discovery quotidien CMDB
  - name: "cmdb-daily-discovery"
    description: "Daily CMDB discovery for all sources"
    type: "cron"
    schedule: "0 2 * * *"  # 2am quotidien
    agents:
      - "sysadmin"
      - "network-engineer"
    action:
      type: "execute"
      command: "/opt/cmdb-discovery/run-discovery.sh"
    timeout: 3600
    retry:
      max_attempts: 3
      delay: 300
    notifications:
      - channel: "telegram"
        on: ["success", "failure"]
      - channel: "email"
        on: ["failure"]
        
  # Health check toutes les 15 minutes
  - name: "system-health-check"
    description: "Check system health"
    type: "interval"
    interval_minutes: 15
    agents:
      - "sysadmin"
    action:
      type: "check"
      checks:
        - "disk-usage"
        - "memory-usage"
        - "service-status"
        
  # Vérification weekly des configs
  - name: "weekly-config-review"
    description: "Weekly review of configurations"
    type: "cron"
    schedule: "0 9 * * 1"  # 9am chaque lundi
    agents:
      - "technical-lead"
      - "network-architect"
    action:
      type: "review"
      items:
        - "firewall-rules"
        - "access-lists"
        - "secrets-expiry"
        
  # Scan vulnérabilités nocturne
  - name: "nightly-vulnerability-scan"
    description: "Run vulnerability scans"
    type: "cron"
    schedule: "0 3 * * *"  # 3am quotidien
    agents:
      - "security"
    action:
      type: "scan"
      targets:
        - "all-hosts"
        - "containers"
    dependencies:
      - "cmdb-daily-discovery"
```

---

## Moteur d'Ordonnancement

```python
#!/usr/bin/env python3
"""Scheduler pour les jobs des agents TI."""

import os
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from croniter import croniter
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobScheduler:
    """Ordonnanceur de jobs pour les agents."""
    
    def __init__(self, config_file='jobs.yaml'):
        self.config_file = config_file
        self.jobs = []
        self.state_file = 'state/state.json'
        self.load_config()
        self.load_state()
        
    def load_config(self):
        """Load jobs configuration."""
        with open(self.config_file) as f:
            config = yaml.safe_load(f)
            self.jobs = config.get('jobs', [])
        logger.info(f"Loaded {len(self.jobs)} jobs")
        
    def load_state(self):
        """Load job state."""
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {}
            
    def save_state(self):
        """Save job state."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def should_run(self, job):
        """Check if job should run now."""
        job_type = job.get('type')
        
        if job_type == 'cron':
            schedule = job.get('schedule')
            return croniter(schedule).is_now()
            
        elif job_type == 'interval':
            interval = job.get('interval_minutes', 60)
            last_run = self.state.get(job['name'], {}).get('last_run')
            
            if not last_run:
                return True
                
            last = datetime.fromisoformat(last_run)
            next_run = last + timedelta(minutes=interval)
            return datetime.now() >= next_run
            
        return False
        
    def execute_job(self, job):
        """Execute a job."""
        logger.info(f"Executing job: {job['name']}")
        
        # Update state
        self.state[job['name']] = {
            'last_run': datetime.now().isoformat(),
            'status': 'running'
        }
        self.save_state()
        
        try:
            action = job.get('action', {})
            
            if action['type'] == 'execute':
                # Execute command
                os.system(action['command'])
                
            elif action['type'] == 'check':
                # Run health check
                logger.info(f"Running checks: {action.get('checks', [])}")
                
            elif action['type'] == 'scan':
                # Run vulnerability scan
                logger.info(f"Scanning: {action.get('targets', [])}")
                
            # Update state
            self.state[job['name']]['status'] = 'success'
            self.state[job['name']]['last_success'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Job failed: {e}")
            self.state[job['name']]['status'] = 'failed'
            self.state[job['name']]['error'] = str(e)
            
        self.save_state()
        
    def run(self):
        """Main scheduler loop."""
        logger.info("Scheduler started")
        
        while True:
            for job in self.jobs:
                if self.should_run(job):
                    # Execute in thread
                    thread = threading.Thread(
                        target=self.execute_job,
                        args=(job,)
                    )
                    thread.start()
                    
            time.sleep(60)  # Check every minute


def main():
    """Main entry point."""
    scheduler = JobScheduler()
    scheduler.run()


if __name__ == '__main__':
    main()
```

---

## Déclencheurs Spéciaux

### Dependency Trigger

```yaml
# triggers/dependency.yaml
dependencies:
  - name: "post-deployment-checks"
    trigger_after:
      - "deployment-complete"
    delay_minutes: 5
    condition: "previous_job.success"
```

### Event Trigger

```yaml
# triggers/event.yaml
event_triggers:
  - name: "incident-response"
    event_type: "servicenow.incident_created"
    filters:
      - field: "impact"
        operator: "<="
        value: 2
    action:
      agents: ["sysadmin", "network-engineer"]
      notify: true
```

---

## State Management

```json
{
  "cmdb-daily-discovery": {
    "last_run": "2026-04-04T02:00:00",
    "last_success": "2026-04-04T02:15:00",
    "status": "success",
    "duration_seconds": 900,
    "records_discovered": 150
  },
  "system-health-check": {
    "last_run": "2026-04-04T22:45:00",
    "status": "success",
    "checks_passed": 12,
    "checks_failed": 0
  }
}
```

---

## Commandes CLI

```bash
# Démarrer le scheduler
python3 scheduler/scheduler.py &

# Lister les jobs
python3 scheduler/scheduler.py --list

# Exécuter un job manuellement
python3 scheduler/scheduler.py --run cmdb-daily-discovery

# Statut des jobs
python3 scheduler/scheduler.py --status

# Arrêter le scheduler
pkill -f scheduler.py
```

---

## Intégration avec les Agents

Les agents peuvent soumettre des jobs:

```python
def schedule_job(name, schedule, agents, action):
    """Schedule a new job."""
    job = {
        'name': name,
        'schedule': schedule,
        'agents': agents,
        'action': action
    }
    
    # Ajouter au fichier jobs.yaml
    with open('jobs.yaml') as f:
        config = yaml.safe_load(f)
        
    config['jobs'].append(job)
    
    with open('jobs.yaml', 'w') as f:
        yaml.dump(config, f)
```

---

*Scheduler pour TI Team Agents*
*Dernière mise à jour: 2026-04-04*