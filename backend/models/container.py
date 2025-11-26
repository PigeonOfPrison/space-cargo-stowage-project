from pydantic import BaseModel, Field
from typing import List, Optional
import math

class Container(BaseModel):
    # Required fields from PDF CSV format
    containerId: str = Field(..., description="Unique container identifier")
    zone: str = Field(..., description="Station zone location")
    width: float = Field(..., gt=0, description="Width in cm (open face dimension)")
    depth: float = Field(..., gt=0, description="Depth in cm (into container)")
    height: float = Field(..., gt=0, description="Height in cm (open face dimension)")
    
    # Operational data
    items: List[str] = Field(default_factory=list, description="List of item IDs")
    
    def get_volume(self) -> float:
        """Total container volume"""
        return self.width * self.depth * self.height
    
    def get_used_volume(self, items_dict: dict) -> float:
        """Calculate currently used volume"""
        used = 0.0
        for item_id in self.items:
            if item_id in items_dict and items_dict[item_id].position:
                pos = items_dict[item_id].position
                start = pos["startCoordinates"]
                end = pos["endCoordinates"]
                item_volume = (
                    (end["width"] - start["width"]) *
                    (end["depth"] - start["depth"]) *
                    (end["height"] - start["height"])
                )
                used += item_volume
        return used
    
    def get_utilization_percentage(self, items_dict: dict) -> float:
        """Get utilization as percentage"""
        total_vol = self.get_volume()
        if total_vol == 0:
            return 0.0
        used_vol = self.get_used_volume(items_dict)
        return (used_vol / total_vol) * 100.0
    
    def get_available_volume(self, items_dict: dict) -> float:
        """Get remaining available volume"""
        return self.get_volume() - self.get_used_volume(items_dict)
    
    def can_fit_item(self, item_volume: float, items_dict: dict) -> bool:
        """Check if item volume can fit in container"""
        return self.get_available_volume(items_dict) >= item_volume
