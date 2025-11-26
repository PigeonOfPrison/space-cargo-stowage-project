from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from backend.models.log_entry import LogEntry
from backend.engines.waste_engine import WasteEngine
from backend.storage.memory_store import storage
import time

router = APIRouter()

# Request/Response models
class ReturnPlanRequest(BaseModel):
    undockingContainerId: str
    undockingDate: str
    maxWeight: float = Field(..., gt=0)

class UndockingRequest(BaseModel):
    undockingContainerId: str
    timestamp: str

class WasteResponse(BaseModel):
    success: bool
    wasteItems: List[Dict]

class ReturnPlanResponse(BaseModel):
    success: bool
    returnPlan: List[Dict]
    retrievalSteps: List[Dict]
    returnManifest: Dict

class UndockingResponse(BaseModel):
    success: bool
    itemsRemoved: int

@router.get("/waste/identify", response_model=WasteResponse)
async def identify_waste():
    """
    Identify all waste items (expired or depleted)
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        current_date = storage.get_simulation_date()
        
        # Identify waste items
        waste_items = waste_engine.identify_waste_items(placed_items, current_date)
        
        # Log waste identification
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="waste_identification",
            itemId=None,
            details={
                "waste_items_found": len(waste_items),
                "simulation_date": current_date.isoformat()
            }
        )
        storage.add_log(log_entry)
        
        return WasteResponse(
            success=True,
            wasteItems=waste_items
        )
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="waste_identification",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Waste identification error: {str(e)}")

@router.post("/waste/return-plan", response_model=ReturnPlanResponse)
async def create_return_plan(request: ReturnPlanRequest):
    """
    Create a return plan for waste items
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        # Validate undocking container
        if request.undockingContainerId not in containers:
            raise HTTPException(
                status_code=404, 
                detail=f"Undocking container {request.undockingContainerId} not found"
            )
        
        # Parse undocking date
        from datetime import datetime
        try:
            undocking_date = datetime.fromisoformat(request.undockingDate)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid undocking date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
        
        # Calculate return plan
        return_plan_data = waste_engine.calculate_return_plan(
            request.undockingContainerId,
            request.maxWeight,
            placed_items,
            containers,
            undocking_date
        )
        
        # Log return plan creation
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="return_plan",
            itemId=None,
            details={
                "undocking_container": request.undockingContainerId,
                "undocking_date": request.undockingDate,
                "max_weight": request.maxWeight,
                "items_in_plan": len(return_plan_data["returnPlan"]),
                "total_weight": return_plan_data["returnManifest"]["totalWeight"],
                "total_volume": return_plan_data["returnManifest"]["totalVolume"]
            }
        )
        storage.add_log(log_entry)
        
        return ReturnPlanResponse(
            success=True,
            returnPlan=return_plan_data["returnPlan"],
            retrievalSteps=return_plan_data["retrievalSteps"],
            returnManifest=return_plan_data["returnManifest"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="return_plan",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "undocking_container": request.undockingContainerId
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Return plan error: {str(e)}")

@router.post("/waste/complete-undocking", response_model=UndockingResponse)
async def complete_undocking(request: UndockingRequest):
    """
    Complete undocking process and remove container with all items
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        # Validate undocking container
        if request.undockingContainerId not in containers:
            raise HTTPException(
                status_code=404,
                detail=f"Undocking container {request.undockingContainerId} not found"
            )
        
        # Execute undocking
        success, items_removed = waste_engine.execute_undocking(
            request.undockingContainerId, placed_items, containers
        )
        
        if success:
            # Log undocking completion
            log_entry = LogEntry(
                timestamp=request.timestamp,
                userId="system",
                actionType="undocking",
                itemId=None,
                details={
                    "undocking_container": request.undockingContainerId,
                    "items_removed": items_removed,
                    "result": "completed"
                }
            )
            storage.add_log(log_entry)
            
            return UndockingResponse(
                success=True,
                itemsRemoved=items_removed
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to complete undocking")
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=request.timestamp,
            userId="system",
            actionType="undocking",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "undocking_container": request.undockingContainerId
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Undocking error: {str(e)}")

@router.get("/waste/statistics")
async def get_waste_statistics():
    """
    Get comprehensive waste statistics
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        current_date = storage.get_simulation_date()
        
        # Get waste statistics
        stats = waste_engine.get_waste_statistics(placed_items, current_date)
        
        return {
            "success": True,
            "statistics": stats,
            "simulation_date": current_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.post("/waste/consolidate")
async def consolidate_waste(target_container_id: str):
    """
    Suggest consolidating waste items into a target container
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        
        # Validate target container
        if target_container_id not in containers:
            raise HTTPException(
                status_code=404,
                detail=f"Target container {target_container_id} not found"
            )
        
        # Get consolidation plan
        consolidation_plan = waste_engine.suggest_waste_consolidation(
            placed_items, containers, target_container_id
        )
        
        # Log consolidation suggestion
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="waste_consolidation",
            itemId=None,
            details={
                "target_container": target_container_id,
                "consolidation_steps": len(consolidation_plan)
            }
        )
        storage.add_log(log_entry)
        
        return {
            "success": True,
            "consolidationPlan": consolidation_plan,
            "targetContainer": target_container_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="waste_consolidation",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "target_container": target_container_id
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Consolidation error: {str(e)}")

@router.get("/waste/predict")
async def predict_future_waste(days_ahead: int = 30):
    """
    Predict items that will become waste in the future
    """
    try:
        from backend.engines.simulation_engine import SimulationEngine
        simulation_engine = SimulationEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        current_date = storage.get_simulation_date()
        
        # Set simulation engine current date
        simulation_engine.set_current_date(current_date)
        
        # Predict future waste
        prediction = simulation_engine.predict_future_waste(placed_items, days_ahead)
        
        return {
            "success": True,
            "prediction": prediction,
            "daysAhead": days_ahead,
            "currentDate": current_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/waste/containers")
async def get_waste_containers():
    """
    Get information about containers that contain waste items
    """
    try:
        waste_engine = WasteEngine()
        
        # Get current storage state
        placed_items = storage.get_all_items()
        containers = storage.get_all_containers()
        current_date = storage.get_simulation_date()
        
        # Identify waste items
        waste_items = waste_engine.identify_waste_items(placed_items, current_date)
        
        # Group by container
        waste_by_container = {}
        for waste_item in waste_items:
            container_id = waste_item["containerId"]
            if container_id not in waste_by_container:
                container = containers.get(container_id)
                waste_by_container[container_id] = {
                    "containerId": container_id,
                    "zone": container.zone if container else "Unknown",
                    "wasteItems": [],
                    "totalWasteVolume": 0.0,
                    "totalWasteMass": 0.0
                }
            
            item = placed_items[waste_item["itemId"]]
            waste_by_container[container_id]["wasteItems"].append(waste_item)
            waste_by_container[container_id]["totalWasteVolume"] += item.get_volume()
            waste_by_container[container_id]["totalWasteMass"] += item.mass
        
        return {
            "success": True,
            "wasteContainers": list(waste_by_container.values()),
            "totalContainersWithWaste": len(waste_by_container)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Waste containers error: {str(e)}")
