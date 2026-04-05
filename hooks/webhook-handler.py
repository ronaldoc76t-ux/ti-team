#!/usr/bin/env python3
"""Webhook Handler pour TI Team Agents."""

import os
import sys
import json
import hmac
import hashlib
import logging
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

EVENTS_FILE = '/tmp/webhook-events.json'


class WebhookHandler(BaseHTTPRequestHandler):
    """Handler pour les webhooks entrants."""
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
        
    def do_POST(self):
        """Handle POST requests."""
        try:
            # Read payload
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length)
            
            # Verify auth
            if not self.verify_auth(payload):
                self.send_error(401, "Unauthorized")
                return
                
            # Parse event type
            event_type = self.get_event_type()
            
            # Process event
            data = json.loads(payload) if payload else {}
            self.route_event(event_type, data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'accepted', 'event': event_type}).encode())
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            self.send_error(500, str(e))
    
    def get_event_type(self):
        """Extract event type from headers."""
        return (
            self.headers.get('X-Gitlab-Event') or
            self.headers.get('X-Jira-Event') or
            self.headers.get('X-ServiceNow-Event') or
            self.headers.get('X-GitHub-Event') or
            self.headers.get('X-Webhook-Type') or
            'unknown'
        )
    
    def verify_auth(self, payload):
        """Verify authentication."""
        secret = os.getenv('WEBHOOK_SECRET', '')
        if not secret:
            return True
            
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
        logger.info(f"Event: {event_type}")
        
        # Load routing config
        config = self.load_config()
        
        # Find matching routes
        routes = config.get('routing', [])
        matched = [r for r in routes if self.match_event(r, event_type, data)]
        
        for route in sorted(matched, key=lambda r: r.get('priority', 0)):
            agents = route.get('agents', [])
            logger.info(f"  → Agents: {agents}")
            
        # Log event
        self.log_event(event_type, data, matched)
    
    def load_config(self):
        """Load webhook configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__), 
            'config.yaml'
        )
        if os.path.exists(config_path):
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def match_event(self, route, event_type, data):
        """Check if route matches event."""
        route_event = route.get('event', '')
        
        # Simple prefix matching
        if route_event.startswith(event_type.split('.')[0]):
            return True
            
        # Exact match
        return route_event == event_type
    
    def log_event(self, event_type, data, routes):
        """Log event for agent polling."""
        event = {
            'timestamp': self.log_timestamp(),
            'type': event_type,
            'data': self.sanitize_data(data),
            'routes': routes
        }
        
        with open(EVENTS_FILE, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def sanitize_data(self, data):
        """Remove sensitive data from event."""
        # Remove passwords, tokens, etc.
        sensitive = ['password', 'token', 'secret', 'api_key']
        if isinstance(data, dict):
            return {k: v for k, v in data.items() 
                    if k.lower() not in sensitive}
        return data
    
    def log_timestamp(self):
        """Get ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def run_server(host, port, config):
    """Run the webhook server."""
    server = HTTPServer((host, port), WebhookHandler)
    logger.info(f"Webhook server listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Webhook Handler')
    parser.add_argument('--host', default='0.0.0.0', help='Host')
    parser.add_argument('--port', type=int, default=8080, help='Port')
    parser.add_argument('--config', default='config.yaml', help='Config file')
    args = parser.parse_args()
    
    run_server(args.host, args.port, args.config)


if __name__ == '__main__':
    main()