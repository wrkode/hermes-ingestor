"""
Audit logging utilities for the Hermes Ingestor.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from ..config import settings

logger = logging.getLogger("audit")

class AuditLogger:
    """Audit logger for tracking security-relevant events."""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # Add file handler for audit logs
        handler = logging.FileHandler(settings.audit_log_path)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_event(self, 
                  event_type: str,
                  user_id: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (e.g., 'login', 'file_upload')
            user_id: ID of the user performing the action
            ip_address: IP address of the request
            details: Additional event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        self.logger.info(json.dumps(event))

# Create audit logger instance
audit_logger = AuditLogger() 