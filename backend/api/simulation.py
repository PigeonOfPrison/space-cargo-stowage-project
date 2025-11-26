from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from backend.models.log_entry import LogEntry
from backend.engines.simulation_engine import SimulationEngine
from backend.storage.memory_store import storage
import time

router = APIRouter()

# Request/Response models
class ItemToUse(BaseModel):
    itemId: Optional[str] = None
    name: Optional[str] = None

class SimulationRequest(BaseModel):
    numOfDays: Optional[int] = Field(None, ge=1, description="Number of days to simulate")
    toTimestamp: Optional[str] = Field(None, description="Target date in ISO format")
    itemsToBeUsedPerDay: List[ItemToUse] = Field(default_factory=list)

class SimulationResponse(BaseModel):
    success: bool
    newDate: str
    changes: Dict

@router.post("/simulate/day", response_model=SimulationResponse)
async def simulate_time(request: SimulationRequest):
    """
    Simulate time progression and item usage
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current simulation date from storage
        current_date = storage.get_simulation_date()
        simulation_engine.set_current_date(current_date)
        
        # Validate request
        if not request.numOfDays and not request.toTimestamp:
            raise HTTPException(
                status_code=400,
                detail="Either numOfDays or toTimestamp must be provided"
            )
        
        if request.numOfDays and request.toTimestamp:
            raise HTTPException(
                status_code=400,
                detail="Provide either numOfDays or toTimestamp, not both"
            )
        
        # Advance time
        if request.numOfDays:
            new_date = simulation_engine.advance_time(num_days=request.numOfDays)
        else:
            new_date = simulation_engine.advance_time(target_date=request.toTimestamp)
        
        # Update storage with new date
        storage.set_simulation_date(new_date)
        
        # Get current items
        placed_items = storage.get_all_items()
        
        # Simulate daily usage
        changes = simulation_engine.simulate_daily_usage(
            request.itemsToBeUsedPerDay, placed_items
        )
        
        # Update items in storage
        for item_info in changes["itemsUsed"]:
            item_id = item_info["itemId"]
            if item_id in placed_items:
                storage.update_item(placed_items[item_id])
        
        # Log simulation
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="simulation",
            itemId=None,
            details={
                "days_simulated": request.numOfDays or "to_target_date",
                "target_date": request.toTimestamp,
                "new_simulation_date": new_date.isoformat(),
                "items_used": len(changes["itemsUsed"]),
                "items_expired": len(changes["itemsExpired"]),
                "items_depleted": len(changes["itemsDepletedToday"]),
                "items_to_use_requested": len(request.itemsToBeUsedPerDay)
            }
        )
        storage.add_log(log_entry)
        
        return SimulationResponse(
            success=True,
            newDate=new_date.isoformat(),
            changes=changes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="simulation",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "request_days": request.numOfDays,
                "request_target": request.toTimestamp
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/simulate/status")
async def get_simulation_status():
    """
    Get current simulation status and statistics
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current state
        current_date = storage.get_simulation_date()
        placed_items = storage.get_all_items()
        
        # Set simulation engine date
        simulation_engine.set_current_date(current_date)
        
        # Get comprehensive statistics
        stats = simulation_engine.get_item_statistics(placed_items)
        
        # Get expiring items (next 7 days)
        expiring_items = simulation_engine.get_expiring_items(placed_items, days_ahead=7)
        
        # Get low usage items
        low_usage_items = simulation_engine.get_low_usage_items(placed_items, threshold=0.8)
        
        return {
            "success": True,
            "currentSimulationDate": current_date.isoformat(),
            "statistics": stats,
            "expiringItems": expiring_items,
            "lowUsageItems": low_usage_items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation status error: {str(e)}")

@router.get("/simulate/expiring")
async def get_expiring_items(days_ahead: int = Query(7, ge=1, le=365)):
    """
    Get items that will expire within specified days
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current state
        current_date = storage.get_simulation_date()
        placed_items = storage.get_all_items()
        
        # Set simulation engine date
        simulation_engine.set_current_date(current_date)
        
        # Get expiring items
        expiring_items = simulation_engine.get_expiring_items(placed_items, days_ahead)
        
        return {
            "success": True,
            "currentDate": current_date.isoformat(),
            "daysAhead": days_ahead,
            "expiringItems": expiring_items,
            "totalExpiringItems": len(expiring_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expiring items error: {str(e)}")

@router.get("/simulate/low-usage")
async def get_low_usage_items(threshold: float = Query(0.8, ge=0.1, le=1.0)):
    """
    Get items that are running low on uses
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current state
        current_date = storage.get_simulation_date()
        placed_items = storage.get_all_items()
        
        # Set simulation engine date
        simulation_engine.set_current_date(current_date)
        
        # Get low usage items
        low_usage_items = simulation_engine.get_low_usage_items(placed_items, threshold)
        
        return {
            "success": True,
            "currentDate": current_date.isoformat(),
            "usageThreshold": threshold,
            "lowUsageItems": low_usage_items,
            "totalLowUsageItems": len(low_usage_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Low usage items error: {str(e)}")

@router.post("/simulate/reset")
async def reset_simulation():
    """
    Reset simulation to current real time
    """
    try:
        from datetime import datetime
        
        # Reset to current time
        current_time = datetime.now()
        storage.set_simulation_date(current_time)
        
        # Log reset
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="simulation_reset",
            itemId=None,
            details={
                "reset_to_date": current_time.isoformat(),
                "reason": "manual_reset"
            }
        )
        storage.add_log(log_entry)
        
        return {
            "success": True,
            "message": "Simulation reset to current time",
            "currentSimulationDate": current_time.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation reset error: {str(e)}")

@router.get("/simulate/predict")
async def predict_future_state(days_ahead: int = Query(30, ge=1, le=365)):
    """
    Predict future state without advancing simulation
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current state
        current_date = storage.get_simulation_date()
        placed_items = storage.get_all_items()
        
        # Set simulation engine date
        simulation_engine.set_current_date(current_date)
        
        # Predict future waste
        waste_prediction = simulation_engine.predict_future_waste(placed_items, days_ahead)
        
        # Get items expiring in the period
        expiring_items = simulation_engine.get_expiring_items(placed_items, days_ahead)
        
        return {
            "success": True,
            "currentDate": current_date.isoformat(),
            "daysAhead": days_ahead,
            "wastePrediction": waste_prediction,
            "expiringItems": expiring_items,
            "summary": {
                "totalItemsNow": len(placed_items),
                "predictedWasteItems": waste_prediction["totalPredictedWaste"],
                "itemsExpiringInPeriod": len(expiring_items)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Future prediction error: {str(e)}")

@router.post("/simulate/bulk-usage")
async def simulate_bulk_usage(items_to_use: List[ItemToUse]):
    """
    Simulate usage of multiple items without advancing time
    """
    try:
        simulation_engine = SimulationEngine()
        
        # Get current state
        current_date = storage.get_simulation_date()
        placed_items = storage.get_all_items()
        
        # Set simulation engine date
        simulation_engine.set_current_date(current_date)
        
        # Simulate usage
        changes = simulation_engine.simulate_daily_usage(items_to_use, placed_items)
        
        # Update items in storage
        for item_info in changes["itemsUsed"]:
            item_id = item_info["itemId"]
            if item_id in placed_items:
                storage.update_item(placed_items[item_id])
        
        # Log bulk usage
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="bulk_usage",
            itemId=None,
            details={
                "items_requested": len(items_to_use),
                "items_used": len(changes["itemsUsed"]),
                "items_depleted": len(changes["itemsDepletedToday"]),
                "simulation_date": current_date.isoformat()
            }
        )
        storage.add_log(log_entry)
        
        return {
            "success": True,
            "changes": changes,
            "simulationDate": current_date.isoformat()
        }
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="bulk_usage",
            itemId=None,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "items_requested": len(items_to_use)
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Bulk usage error: {str(e)}")
