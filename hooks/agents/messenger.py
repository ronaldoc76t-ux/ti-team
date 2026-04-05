#!/usr/bin/env python3
"""Messenger pour communication inter-agents TI-Team."""

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
        
        inbox = self.BASE_DIR / to_agent
        inbox.mkdir(parents=True, exist_ok=True)
        
        msg_file = inbox / f"{msg['id']}.json"
        with open(msg_file, 'w') as f:
            json.dump(msg, f, indent=2)
            
        print(f"[{self.agent_name} → {to_agent}] {message}")
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


def send_to_agent(from_agent, to_agent, message, **kwargs):
    """Envoyer un message."""
    messenger = InterAgentMessenger(from_agent)
    return messenger.send(to_agent, message, **kwargs)


def check_inbox(agent_name):
    """Vérifier la boîte de réception."""
    messenger = InterAgentMessenger(agent_name)
    return messenger.receive()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: messenger.py <from_agent> <to_agent> <message>")
        sys.exit(1)
        
    from_agent = sys.argv[1]
    to_agent = sys.argv[2]
    message = ' '.join(sys.argv[3:])
    
    send_to_agent(from_agent, to_agent, message)