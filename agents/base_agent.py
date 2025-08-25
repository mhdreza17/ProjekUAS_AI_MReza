from datetime import datetime
import logging

class BaseAgent:
    """Base class untuk semua agent dengan enhanced logging dan status tracking"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.status = "initialized"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.activity_log = []
        self.error_count = 0
        
        # Setup logger
        self.logger = logging.getLogger(f"agents.{agent_name.lower()}")
        self.logger.setLevel(logging.INFO)
        
        self.log_action("Agent initialized", f"Agent: {agent_name}")
    
    def set_status(self, status: str):
        """Set agent status dengan timestamp"""
        old_status = self.status
        self.status = status
        self.last_activity = datetime.now()
        
        if status == "error":
            self.error_count += 1
        
        self.log_action("Status changed", f"{old_status} -> {status}")
    
    def get_status(self) -> dict:
        """Get comprehensive agent status"""
        uptime = (datetime.now() - self.created_at).total_seconds()
        
        return {
            "agent_name": self.agent_name,
            "current_status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "uptime_seconds": uptime,
            "error_count": self.error_count,
            "total_activities": len(self.activity_log),
            "recent_activities": self.activity_log[-5:] if self.activity_log else []
        }
    
    def log_action(self, action: str, details: str = ""):
        """Enhanced logging with structured format"""
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "action": action,
            "details": details,
            "status": self.status
        }
        
        # Add to activity log (keep last 100 entries)
        self.activity_log.append(log_entry)
        if len(self.activity_log) > 100:
            self.activity_log = self.activity_log[-100:]
        
        # Log to system logger
        log_message = f"[{self.agent_name}] {action}"
        if details:
            log_message += f" - {details}"
        
        if self.status == "error":
            self.logger.error(log_message)
        elif action.upper().startswith("WARNING"):
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def get_activity_summary(self) -> dict:
        """Get activity summary for monitoring"""
        if not self.activity_log:
            return {"message": "No activities recorded"}
        
        recent_actions = [entry["action"] for entry in self.activity_log[-10:]]
        error_actions = [entry for entry in self.activity_log if "error" in entry["action"].lower()]
        
        return {
            "total_activities": len(self.activity_log),
            "recent_actions": recent_actions,
            "error_count": len(error_actions),
            "last_error": error_actions[-1] if error_actions else None,
            "status_distribution": self._get_status_distribution()
        }
    
    def _get_status_distribution(self) -> dict:
        """Get distribution of statuses over time"""
        status_counts = {}
        for entry in self.activity_log:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return status_counts
    
    def reset_error_count(self):
        """Reset error count (useful for health monitoring)"""
        old_count = self.error_count
        self.error_count = 0
        self.log_action("Error count reset", f"Was: {old_count}")
    
    def is_healthy(self) -> bool:
        """Check if agent is in healthy state"""
        # Consider agent unhealthy if too many errors recently
        recent_errors = [
            entry for entry in self.activity_log[-20:] 
            if "error" in entry["action"].lower()
        ]
        
        return len(recent_errors) < 5 and self.status != "error"
    
    def process(self, *args, **kwargs):
        """Base process method - should be overridden by subclasses"""
        raise NotImplementedError(f"Process method must be implemented by {self.agent_name}")
    
    def cleanup(self):
        """Cleanup method for graceful shutdown"""
        self.log_action("Agent cleanup initiated", "Performing cleanup operations")
        self.set_status("cleaning_up")
        
        # Subclasses can override this method for specific cleanup
        # Base implementation just logs the activity
        
        self.set_status("cleaned_up")
        self.log_action("Agent cleanup completed", "Agent ready for shutdown")