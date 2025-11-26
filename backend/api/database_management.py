from fastapi import APIRouter, HTTPException
from backend.storage.memory_store import storage
from backend.models.item import Item
from backend.models.container import Container
import time

router = APIRouter()

@router.post("/database/clear")
async def clear_database():
    """
    Clear all data from the database
    Useful for testing, evaluation, or starting fresh
    """
    try:
        start_time = time.time()
        
        # Clear all data
        success = storage.clear()
        
        if success:
            processing_time = round((time.time() - start_time) * 1000, 2)
            return {
                "success": True,
                "message": "Database cleared successfully",
                "details": {
                    "items_cleared": True,
                    "containers_cleared": True,
                    "logs_cleared": True,
                    "simulation_reset": True,
                    "processing_time_ms": processing_time
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database clear error: {str(e)}")

@router.get("/database/status")
async def get_database_status():
    """
    Get current database status and statistics
    """
    try:
        items = storage.get_all_items()
        containers = storage.get_all_containers()
        logs = storage.get_all_logs()
        
        # Calculate placement statistics
        placed_items = len([item for item in items.values() if item.containerId])
        unplaced_items = len(items) - placed_items
        
        # Calculate container utilization
        container_stats = []
        for container in containers.values():
            item_count = len([item for item in items.values() if item.containerId == container.containerId])
            container_stats.append({
                "containerId": container.containerId,
                "zone": container.zone,
                "itemCount": item_count,
                "dimensions": f"{container.width}x{container.depth}x{container.height}"
            })
        
        return {
            "success": True,
            "database_status": {
                "items": {
                    "total": len(items),
                    "placed": placed_items,
                    "unplaced": unplaced_items
                },
                "containers": {
                    "total": len(containers),
                    "details": container_stats
                },
                "logs": {
                    "total": len(logs)
                },
                "simulation": {
                    "current_date": storage.get_simulation_date().isoformat()
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database status error: {str(e)}")

@router.post("/database/reset")
async def reset_database():
    """
    Reset database to initial state
    Clears all data and resets simulation to current time
    """
    try:
        start_time = time.time()
        
        # Clear and reset
        success = storage.clear()
        
        if success:
            processing_time = round((time.time() - start_time) * 1000, 2)
            return {
                "success": True,
                "message": "Database reset to initial state",
                "details": {
                    "all_data_cleared": True,
                    "simulation_reset_to_now": True,
                    "processing_time_ms": processing_time
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset database")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reset error: {str(e)}")
