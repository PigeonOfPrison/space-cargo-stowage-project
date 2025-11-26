from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from backend.models.item import Item
from backend.models.log_entry import LogEntry
from backend.engines.retrieval_engine import RetrievalEngine
from backend.storage.memory_store import storage
import time

router = APIRouter()

# Request/Response models
class RetrieveRequest(BaseModel):
    itemId: str
    userId: Optional[str] = None
    timestamp: Optional[str] = None

class PlaceRequest(BaseModel):
    itemId: str
    userId: Optional[str] = None
    timestamp: Optional[str] = None
    containerId: str
    position: Dict

class SearchResponse(BaseModel):
    success: bool
    found: bool
    item: Optional[Dict] = None
    retrievalSteps: Optional[List[Dict]] = []

class ActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@router.get("/search", response_model=SearchResponse)
async def search_item(
    itemId: Optional[str] = Query(None, description="Item ID to search for"),
    itemName: Optional[str] = Query(None, description="Item name to search for"),
    userId: Optional[str] = Query(None, description="User ID for logging")
):
    """
    Search for an item by ID or name and get retrieval instructions
    """
    try:
        if not itemId and not itemName:
            raise HTTPException(status_code=400, detail="Either itemId or itemName must be provided")
        
        retrieval_engine = RetrievalEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        # Find item
        target_item = None
        
        if itemId:
            # Format item ID
            from backend.utils.validators import validate_item_id
            formatted_id = validate_item_id(itemId)
            target_item = retrieval_engine.find_item_by_id(formatted_id, placed_items)
        
        if not target_item and itemName:
            # Find best item by name
            target_item = retrieval_engine.find_best_item_to_retrieve(
                itemName, placed_items, containers
            )
        
        if not target_item:
            # Log failed search
            log_entry = LogEntry(
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
                userId=userId,
                actionType="search",
                itemId=itemId or itemName,
                details={
                    "result": "not_found",
                    "search_type": "id" if itemId else "name"
                }
            )
            storage.add_log(log_entry)
            
            return SearchResponse(
                success=True,
                found=False,
                item=None,
                retrievalSteps=[]
            )
        
        # Check if item is placed
        if not target_item.containerId or not target_item.position:
            return SearchResponse(
                success=True,
                found=True,
                item={
                    "itemId": target_item.itemId,
                    "name": target_item.name,
                    "containerId": None,
                    "zone": None,
                    "position": None
                },
                retrievalSteps=[{
                    "step": 1,
                    "action": "retrieve",
                    "itemId": target_item.itemId,
                    "itemName": target_item.name
                }]
            )
        
        # Get container info
        container = storage.get_container(target_item.containerId)
        if not container:
            raise HTTPException(status_code=500, detail="Container not found")
        
        # Calculate retrieval steps
        retrieval_steps = retrieval_engine.get_retrieval_steps(
            target_item, placed_items, containers
        )
        
        # Log successful search
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId=userId,
            actionType="search",
            itemId=target_item.itemId,
            details={
                "result": "found",
                "search_type": "id" if itemId else "name",
                "container": target_item.containerId,
                "zone": container.zone,
                "retrieval_steps_count": len(retrieval_steps)
            }
        )
        storage.add_log(log_entry)
        
        return SearchResponse(
            success=True,
            found=True,
            item={
                "itemId": target_item.itemId,
                "name": target_item.name,
                "containerId": target_item.containerId,
                "zone": container.zone,
                "position": target_item.position
            },
            retrievalSteps=retrieval_steps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId=userId,
            actionType="search",
            itemId=itemId or itemName,
            details={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/retrieve", response_model=ActionResponse)
async def retrieve_item(request: RetrieveRequest):
    """
    Retrieve an item and update its usage count
    """
    try:
        retrieval_engine = RetrievalEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        # Format item ID
        from backend.utils.validators import validate_item_id
        formatted_id = validate_item_id(request.itemId)
        
        # Simulate retrieval
        success, message, item = retrieval_engine.simulate_retrieval(
            formatted_id, request.userId or "unknown", placed_items, containers
        )
        
        if success and item:
            # Update item in storage
            storage.update_item(item)
            
            # Log retrieval
            log_entry = LogEntry.create_retrieval_log(
                item.itemId, item.containerId, request.userId
            )
            storage.add_log(log_entry)
            
            return ActionResponse(
                success=True,
                message=f"Item {item.name} retrieved successfully. Remaining uses: {item.usageLimit - item.currentUses}"
            )
        else:
            # Log failed retrieval
            log_entry = LogEntry(
                timestamp=request.timestamp or time.strftime("%Y-%m-%dT%H:%M:%S"),
                userId=request.userId,
                actionType="retrieval",
                itemId=formatted_id,
                details={
                    "result": "failed",
                    "reason": message
                }
            )
            storage.add_log(log_entry)
            
            return ActionResponse(
                success=False,
                message=message
            )
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=request.timestamp or time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId=request.userId,
            actionType="retrieval",
            itemId=request.itemId,
            details={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@router.post("/place", response_model=ActionResponse)
async def place_item(request: PlaceRequest):
    """
    Place an item back in a container (after retrieval)
    """
    try:
        # Get item
        from backend.utils.validators import validate_item_id
        formatted_id = validate_item_id(request.itemId)
        
        item = storage.get_item(formatted_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {formatted_id} not found")
        
        # Get container
        container = storage.get_container(request.containerId)
        if not container:
            raise HTTPException(status_code=404, detail=f"Container {request.containerId} not found")
        
        # Validate position
        from backend.utils.validators import validate_coordinates
        validate_coordinates(request.position)
        
        # Validate placement using spatial engine
        from backend.engines.spatial_engine import SpatialEngine
        spatial_engine = SpatialEngine()
        
        placed_items = storage.get_all_items()
        is_valid, error_msg = spatial_engine.validate_placement(
            item, container, request.position, placed_items
        )
        
        if not is_valid:
            return ActionResponse(
                success=False,
                message=f"Invalid placement: {error_msg}"
            )
        
        # Update item placement
        old_container = item.containerId
        item.containerId = request.containerId
        item.position = request.position
        item.placementTimestamp = request.timestamp or time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Update storage
        storage.update_item(item)
        
        # Update container item lists
        if old_container and old_container != request.containerId:
            old_cont = storage.get_container(old_container)
            if old_cont and item.itemId in old_cont.items:
                old_cont.items.remove(item.itemId)
                storage.update_container(old_cont)
        
        if item.itemId not in container.items:
            container.items.append(item.itemId)
            storage.update_container(container)
        
        # Log placement
        if old_container and old_container != request.containerId:
            log_entry = LogEntry.create_rearrangement_log(
                item.itemId, old_container, request.containerId, request.userId
            )
        else:
            log_entry = LogEntry.create_placement_log(
                item.itemId, request.containerId, request.userId
            )
        
        storage.add_log(log_entry)
        
        return ActionResponse(
            success=True,
            message=f"Item {item.name} placed successfully in {request.containerId}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=request.timestamp or time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId=request.userId,
            actionType="placement",
            itemId=request.itemId,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "container": request.containerId
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Placement error: {str(e)}")

@router.get("/search/suggestions")
async def get_search_suggestions(query: str = Query(..., min_length=1)):
    """
    Get search suggestions based on partial item names
    """
    try:
        placed_items = storage.get_all_items()
        
        suggestions = []
        query_lower = query.lower()
        
        for item in placed_items.values():
            if query_lower in item.name.lower():
                suggestions.append({
                    "itemId": item.itemId,
                    "name": item.name,
                    "zone": item.preferredZone,
                    "isPlaced": bool(item.containerId),
                    "priority": item.priority
                })
        
        # Sort by priority (high priority first) and then by name
        suggestions.sort(key=lambda x: (-x["priority"], x["name"]))
        
        # Limit to top 10 suggestions
        return {
            "success": True,
            "suggestions": suggestions[:10]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestions error: {str(e)}")

@router.get("/items/status")
async def get_items_status():
    """
    Get status overview of all items
    """
    try:
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        from datetime import datetime
        current_date = storage.get_simulation_date()
        
        status_counts = {
            "total": len(placed_items),
            "placed": 0,
            "unplaced": 0,
            "active": 0,
            "expired": 0,
            "depleted": 0,
            "by_zone": {}
        }
        
        for item in placed_items.values():
            # Placement status
            if item.containerId:
                status_counts["placed"] += 1
                
                # Zone counting
                container = containers.get(item.containerId)
                if container:
                    zone = container.zone
                    if zone not in status_counts["by_zone"]:
                        status_counts["by_zone"][zone] = 0
                    status_counts["by_zone"][zone] += 1
            else:
                status_counts["unplaced"] += 1
            
            # Item status
            status = item.get_status(current_date)
            if status.value == "active":
                status_counts["active"] += 1
            elif status.value == "expired":
                status_counts["expired"] += 1
            elif status.value == "depleted":
                status_counts["depleted"] += 1
        
        return {
            "success": True,
            "status": status_counts,
            "simulation_date": current_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")
