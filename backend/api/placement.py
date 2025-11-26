from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from backend.models.item import Item
from backend.models.container import Container
from backend.models.log_entry import LogEntry
from backend.engines.advanced_placement_engine import AdvancedPlacementEngine
from backend.engines.ultra_advanced_placement_engine import UltraAdvancedPlacementEngine
from backend.storage.memory_store import storage
from backend.utils.validators import ValidationError
import time

router = APIRouter()

# Request/Response models
class ItemRequest(BaseModel):
    itemId: str
    name: str
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    priority: int = Field(..., ge=1, le=100)
    preferredZone: str
    
    # Optional fields with defaults
    mass: float = Field(default=1.0, gt=0)
    expiryDate: Optional[str] = None
    usageLimit: int = Field(default=100, gt=0)

class ContainerRequest(BaseModel):
    containerId: str
    zone: str
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    height: float = Field(..., gt=0)

class PlacementRequest(BaseModel):
    items: List[ItemRequest]
    containers: List[ContainerRequest]

class PlacementResponse(BaseModel):
    success: bool
    placements: List[Dict]
    rearrangements: Optional[List[Dict]] = []

@router.post("/placement", response_model=PlacementResponse)
async def place_items(request: PlacementRequest):
    """
    Place items in containers with optimal positioning
    """
    try:
        start_time = time.time()
        
        # Initialize optimized placement engine
        placement_engine = AdvancedPlacementEngine()
        
        # Get current storage state
        existing_items = storage.get_all_items()
        existing_containers = storage.get_all_containers()
        
        # Update containers from request
        container_dict = {}
        for container_req in request.containers:
            container = Container(
                containerId=container_req.containerId,
                zone=container_req.zone,
                width=container_req.width,
                depth=container_req.depth,
                height=container_req.height
            )
            container_dict[container.containerId] = container
            
            # Add to storage if new
            if not storage.get_container(container.containerId):
                storage.add_container(container)
        
        print(f"DEBUG: Received {len(container_dict)} containers: {list(container_dict.keys())}")
        
        # Use existing containers if not provided in request
        if not container_dict:
            container_dict = existing_containers
            print(f"DEBUG: Using existing containers: {list(container_dict.keys())}")
        else:
            # Merge with existing containers
            for cid, container in existing_containers.items():
                if cid not in container_dict:
                    container_dict[cid] = container
            print(f"DEBUG: Final container count: {len(container_dict)}")
            
        # Initialize items list
        new_items = []
            
        print(f"DEBUG: Received {len(request.items)} items")
        for item_req in request.items:
            try:
                # Format item ID
                from backend.utils.validators import validate_item_id
                formatted_id = validate_item_id(item_req.itemId)
                
                item = Item(
                    itemId=formatted_id,
                    name=item_req.name,
                    width=item_req.width,
                    depth=item_req.depth,
                    height=item_req.height,
                    mass=item_req.mass,
                    priority=item_req.priority,
                    expiryDate=item_req.expiryDate if item_req.expiryDate != "N/A" else None,
                    usageLimit=item_req.usageLimit,
                    preferredZone=item_req.preferredZone
                )
                new_items.append(item)
                
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=f"Invalid item {item_req.itemId}: {str(e)}")
        
        # Sort items by priority (high priority first)
        new_items.sort(key=lambda x: x.get_priority_score(), reverse=True)
        
        # Use enhanced evaluation method for better optimization
        placements = placement_engine.place_items_enhanced_priority(new_items, container_dict)
        
        # Store successful placements
        for placement in placements:
            item_id = placement["itemId"]
            container_id = placement["containerId"]
            position = placement["position"]
            
            # Find the item
            item = next((item for item in new_items if item.itemId == item_id), None)
            if item:
                # Update item with placement info
                item.containerId = container_id
                item.position = position
                item.placementTimestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
                
                # Add to storage
                existing_item = storage.get_item(item.itemId)
                if existing_item:
                    storage.update_item(item)
                else:
                    storage.add_item(item)
                
                # Update container's item list
                container = storage.get_container(container_id)
                if container and item.itemId not in container.items:
                    container.items.append(item.itemId)
                    storage.update_container(container)
                
                # Log placement
                log_entry = LogEntry.create_placement_log(item.itemId, container_id)
                storage.add_log(log_entry)
        
        successful_placements = len(placements)
        rearrangements_count = 0  # Set to 0 for now
        rearrangements = []  # Initialize rearrangements list
        
        elapsed_time = time.time() - start_time
        
        # Log performance
        performance_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="placement",
            itemId=None,
            details={
                "items_processed": len(new_items),
                "successful_placements": successful_placements,
                "rearrangements_suggested": rearrangements_count,
                "processing_time_seconds": round(elapsed_time, 3)
            }
        )
        storage.add_log(performance_log)
        
        return PlacementResponse(
            success=True,
            placements=placements,
            rearrangements=rearrangements
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="placement",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Placement error: {str(e)}")

@router.get("/placement/validate")
async def validate_placement_request(item_count: int = 1, container_count: int = 1):
    """
    Validate placement request format and provide sample data
    """
    try:
        sample_items = []
        sample_containers = []
        
        # Generate sample items
        for i in range(min(item_count, 5)):  # Limit to 5 samples
            sample_items.append({
                "itemId": f"00000{i+1}",
                "name": f"Sample_Item_{i+1}",
                "width": 10.0 + i,
                "depth": 10.0 + i,
                "height": 20.0 + i,
                "mass": 5.0 + i,
                "priority": 80 - i * 10,
                "expiryDate": "2025-12-31" if i % 2 == 0 else None,
                "usageLimit": 30 + i * 10,
                "preferredZone": ["Crew_Quarters", "Medical_Bay", "Lab", "Storage_Bay", "Airlock"][i]
            })
        
        # Generate sample containers
        zones = ["Crew_Quarters", "Medical_Bay", "Lab", "Storage_Bay", "Airlock"]
        for i in range(min(container_count, 5)):  # Limit to 5 samples
            sample_containers.append({
                "containerId": f"CONT_{chr(65+i)}01",
                "zone": zones[i],
                "width": 100.0,
                "depth": 85.0,
                "height": 200.0
            })
        
        return {
            "success": True,
            "sample_request": {
                "items": sample_items,
                "containers": sample_containers
            },
            "notes": [
                "itemId should be unique and will be zero-padded to 6 digits",
                "priority should be between 1-100 (higher = more important)",
                "expiryDate should be in ISO format or null/N/A",
                "preferredZone should match container zones for optimal placement",
                "All dimensions are in centimeters",
                "Mass is in kilograms"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
