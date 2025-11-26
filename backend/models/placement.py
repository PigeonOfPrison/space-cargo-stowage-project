from pydantic import BaseModel, Field
from typing import Dict, Optional

class Placement(BaseModel):
    """Represents the placement of an item in a container"""
    itemId: str = Field(..., description="Item identifier")
    containerId: str = Field(..., description="Container identifier")
    position: Dict = Field(..., description="Start and end coordinates")
    rotation_used: Optional[tuple] = Field(None, description="Dimensions used (w,d,h)")
    timestamp: Optional[str] = Field(None, description="Placement timestamp")
    userId: Optional[str] = Field(None, description="User who placed the item")
    
    def to_api_format(self) -> Dict:
        """Convert to API response format"""
        return {
            "itemId": self.itemId,
            "containerId": self.containerId,
            "position": self.position
        }
