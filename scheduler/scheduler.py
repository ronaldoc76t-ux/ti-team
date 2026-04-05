#!/usr/bin/env python3
"""Scheduler pour les jobs des agents TI."""

import os
import sys
import json
import time
import logging
import threading
import argparse
import signal
from datetime import datetime, timedelta
from pathlib import Path

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
STATE_FILE = BASE_DIR / 'state' / 'state.json'


class JobScheduler:
    """Ordonnanceur de jobs pour les agents."""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or str(BASE_DIR / 'jobs.yaml')
        self.jobs = []
        self.state = {}
        self.running = True
        self.load_config()
        self.load_state()
        
    def load_config(self):
        """Load jobs configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                config = yaml.safe_load(f)
                self.jobs = config.get('jobs', [])
            logger.info(f"Loaded {len(self.jobs)} jobs")
        else:
            logger.warning(f"Config file not found: {self.config_file}")
            self.jobs = []
        
    def load_state(self):
        """Load job state."""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                self.state = json.load(f)
        else:
            self.state = {}
            
    def save_state(self):
        """Save job state."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def should_run(self, job):
        """Check if job should run now."""
        job_type = job.get('type')
        
        if job_type == 'cron':
            return self.is_cron_now(job.get('schedule', ''))
            
        elif job_type == 'interval':
            return self.should_run_interval(job)
            
        return False
    
    def is_cron_now(self, schedule):
        """Check if cron expression matches now."""
        try:
            from croniter import croniter
            return croniter(schedule).is_now()
        except ImportError:
            # Fallback simple pour les cron standards
            return self.simple_cron_check(schedule)
        except Exception:
            return False
    
    def simple_cron_check(self, schedule):
        """Simple cron check (minute level)."""
        if not schedule:
            return False
        parts = schedule.split()
        if len(parts) >= 1:
            minute = parts[0]
            current_minute = datetime.now().minute
            if minute == '*':
                return True
            if minute.isdigit() and int(minute) == current_minute:
                return True
        return False
            
    def should_run_interval(self, job):
        """Check if interval job should run."""
        interval = job.get('interval_minutes', 60)
        last_run = self.state.get(job['name'], {}).get('last_run')
        
        if not last_run:
            return True
            
        last = datetime.fromisoformat(last_run)
        next_run = last + timedelta(minutes=interval)
        return datetime.now() >= next_run
        
    def execute_job(self, job):
        """Execute a job."""
        name = job['name']
        logger.info(f"Executing: {name}")
        
        # Update state
        self.state[name] = {
            'last_run': datetime.now().isoformat(),
            'status': 'running'
        }
        self.save_state()
        
        try:
            action = job.get('action', {})
            action_type = action.get('type')
            
            if action_type == 'execute':
                result = os.system(action.get('command', 'true'))
                logger.info(f"Command exit code: {result}")
                
            elif action_type == 'check':
                checks = action.get('checks', [])
                logger.info(f"Running checks: {checks}")
                # Placeholder for actual checks
                
            elif action_type == 'scan':
                targets = action.get('targets', [])
                logger.info(f"Scanning: {targets}")
                # Placeholder for actual scans
                
            elif action_type == 'notify':
                logger.info(f"Sending notification: {action.get('message', '')}")
            
            # Success
            self.state[name]['status'] = 'success'
            self.state[name]['last_success'] = datetime.now().isoformat()
            logger.info(f"Job completed: {name}")
            
        except Exception as e:
            logger.error(f"Job failed: {name} - {e}")
            self.state[name]['status'] = 'failed'
            self.state[name]['error'] = str(e)
            
        self.save_state()
        
    def run(self):
        """Main scheduler loop."""
        logger.info("Scheduler started")
        signal.signal(signal.SIGTERM, lambda s, f: setattr(self, 'running', False))
        
        while self.running:
            # Reload config periodically
            if int(time.time()) % 60 == 0:
                self.load_config()
                
            for job in self.jobs:
                if self.should_run(job):
                    thread = threading.Thread(
                        target=self.execute_job,
                        args=(job,),
                        daemon=True
                    )
                    thread.start()
                    
            time.sleep(30)  # Check every 30 seconds
            
        logger.info("Scheduler stopped")
    
    def list_jobs(self):
        """List all jobs."""
        print("\nJobs configured:")
        print("-" * 60)
        for job in self.jobs:
            status = self.state.get(job['name'], {}).get('status', 'never run')
            last = self.state.get(job['name'], {}).get('last_run', 'never')
            print(f"  {job['name']}")
            print(f"    Type: {job.get('type')} | Schedule: {job.get('schedule') or job.get('interval_minutes')}")
            print(f"    Status: {status} | Last run: {last}")
            print(f"    Agents: {', '.join(job.get('agents', []))}")
            print()
    
    def show_status(self):
        """Show job status."""
        print("\nJob Status:")
        print("-" * 60)
        for name, data in self.state.items():
            status = data.get('status', 'unknown')
            last = data.get('last_run', 'never')
            print(f"  {name}: {status} (last: {last})")
        print()
    
    def run_job(self, job_name):
        """Run a specific job manually."""
        for job in self.jobs:
            if job['name'] == job_name:
                self.execute_job(job)
                return
        logger.error(f"Job not found: {job_name}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Job Scheduler')
    parser.add_argument('--config', help='Config file')
    parser.add_argument('--list', action='store_true', help='List jobs')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--run', metavar='JOB', help='Run specific job')
    args = parser.parse_args()
    
    scheduler = JobScheduler(args.config)
    
    if args.list:
        scheduler.list_jobs()
    elif args.status:
        scheduler.show_status()
    elif args.run:
        scheduler.run_job(args.run)
    else:
        scheduler.run()


if __name__ == '__main__':
    main()