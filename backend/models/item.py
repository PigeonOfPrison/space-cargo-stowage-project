from pydantic import BaseModel, Field
from typing import Optional, Tuple, List
from datetime import datetime
from enum import Enum

class ItemStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired" 
    DEPLETED = "depleted"
    WASTE = "waste"

class Item(BaseModel):
    # Required fields from PDF CSV format
    itemId: str = Field(..., description="6-digit zero-padded ID")
    name: str
    width: float = Field(..., gt=0, description="Width in cm")
    depth: float = Field(..., gt=0, description="Depth in cm") 
    height: float = Field(..., gt=0, description="Height in cm")
    priority: int = Field(..., ge=1, le=100, description="Priority 1-100")
    preferredZone: str = Field(..., description="Preferred storage zone")
    
    # Optional fields with defaults
    mass: float = Field(default=1.0, gt=0, description="Mass in kg")
    expiryDate: Optional[str] = Field(None, description="ISO format or N/A")
    usageLimit: int = Field(default=100, gt=0, description="Maximum uses")
    
    # Placement information (set when placed)
    containerId: Optional[str] = None
    position: Optional[dict] = None  # {startCoordinates: {}, endCoordinates: {}}
    currentUses: int = Field(default=0, description="Current usage count")
    placementTimestamp: Optional[str] = None
    
    def get_rotations(self) -> List[Tuple[float, float, float]]:
        """Returns possible 90-degree rotations as per PDF spec"""
        return [
            (self.width, self.depth, self.height),    # 0° (original)
            (self.depth, self.width, self.height),    # 90° rotation
        ]
    
    def get_volume(self) -> float:
        """Calculate item volume"""
        return self.width * self.depth * self.height
    
    def is_expired(self, current_date: datetime) -> bool:
        """Check if item is expired based on current simulation date"""
        if not self.expiryDate or self.expiryDate == "N/A":
            return False
        try:
            expiry = datetime.fromisoformat(self.expiryDate)
            return current_date > expiry
        except:
            return False
    
    def is_depleted(self) -> bool:
        """Check if item has reached usage limit"""
        return self.currentUses >= self.usageLimit
    
    def get_status(self, current_date: datetime) -> ItemStatus:
        """Get current item status"""
        if self.is_expired(current_date):
            return ItemStatus.EXPIRED
        elif self.is_depleted():
            return ItemStatus.DEPLETED
        else:
            return ItemStatus.ACTIVE
    
    def get_priority_score(self) -> float:
        """Calculate priority score for placement optimization"""
        # High priority items get preference for accessible locations
        base_score = self.priority
        
        # Boost score for critical zones
        critical_zones = ["Medical_Bay", "Life_Support", "Command_Center"]
        if self.preferredZone in critical_zones:
            base_score += 20
            
        return base_score
