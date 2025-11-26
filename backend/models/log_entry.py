from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class LogEntry(BaseModel):
    """Represents a log entry for system actions"""
    timestamp: str = Field(..., description="ISO format timestamp")
    userId: Optional[str] = Field(None, description="User identifier")
    actionType: str = Field(..., description="Type of action performed")
    itemId: Optional[str] = Field(None, description="Item identifier")
    details: Dict = Field(default_factory=dict, description="Additional details")
    
    @classmethod
    def create_placement_log(cls, item_id: str, container_id: str, user_id: str = None) -> 'LogEntry':
        """Create a placement log entry"""
        return cls(
            timestamp=datetime.now().isoformat(),
            userId=user_id,
            actionType="placement",
            itemId=item_id,
            details={
                "toContainer": container_id,
                "reason": "Item placement"
            }
        )
    
    @classmethod
    def create_retrieval_log(cls, item_id: str, container_id: str, user_id: str = None) -> 'LogEntry':
        """Create a retrieval log entry"""
        return cls(
            timestamp=datetime.now().isoformat(),
            userId=user_id,
            actionType="retrieval",
            itemId=item_id,
            details={
                "fromContainer": container_id,
                "reason": "Item retrieval"
            }
        )
    
    @classmethod
    def create_rearrangement_log(cls, item_id: str, from_container: str, to_container: str, user_id: str = None) -> 'LogEntry':
        """Create a rearrangement log entry"""
        return cls(
            timestamp=datetime.now().isoformat(),
            userId=user_id,
            actionType="rearrangement",
            itemId=item_id,
            details={
                "fromContainer": from_container,
                "toContainer": to_container,
                "reason": "Space optimization"
            }
        )
    
    @classmethod
    def create_disposal_log(cls, item_id: str, container_id: str, reason: str, user_id: str = None) -> 'LogEntry':
        """Create a disposal log entry"""
        return cls(
            timestamp=datetime.now().isoformat(),
            userId=user_id,
            actionType="disposal",
            itemId=item_id,
            details={
                "fromContainer": container_id,
                "reason": reason
            }
        )
