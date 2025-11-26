from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.storage.memory_store import storage

router = APIRouter()

# Response models
class LogsResponse(BaseModel):
    logs: List[Dict]

@router.get("/logs", response_model=LogsResponse)
async def get_logs(
    startDate: Optional[str] = Query(None, description="Start date in ISO format"),
    endDate: Optional[str] = Query(None, description="End date in ISO format"),
    itemId: Optional[str] = Query(None, description="Filter by item ID"),
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    actionType: Optional[str] = Query(None, description="Filter by action type"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of logs to return")
):
    """
    Retrieve logs with optional filtering
    """
    try:
        # Get logs from storage with filters
        logs = storage.get_logs(
            start_date=startDate,
            end_date=endDate,
            item_id=itemId,
            user_id=userId,
            action_type=actionType
        )
        
        # Limit results
        if limit and len(logs) > limit:
            logs = logs[:limit]
        
        # Convert to dict format
        log_dicts = []
        for log in logs:
            log_dict = {
                "timestamp": log.timestamp,
                "userId": log.userId,
                "actionType": log.actionType,
                "itemId": log.itemId,
                "details": log.details
            }
            log_dicts.append(log_dict)
        
        return LogsResponse(logs=log_dicts)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logs retrieval error: {str(e)}")

@router.get("/logs/summary")
async def get_logs_summary():
    """
    Get summary statistics of log entries
    """
    try:
        # Get all logs
        all_logs = storage.get_logs()
        
        # Calculate statistics
        total_logs = len(all_logs)
        action_counts = {}
        user_counts = {}
        recent_activity = []
        
        for log in all_logs:
            # Count by action type
            action_type = log.actionType
            if action_type not in action_counts:
                action_counts[action_type] = 0
            action_counts[action_type] += 1
            
            # Count by user
            user_id = log.userId or "system"
            if user_id not in user_counts:
                user_counts[user_id] = 0
            user_counts[user_id] += 1
        
        # Get recent activity (last 10 logs)
        recent_logs = all_logs[:10]
        for log in recent_logs:
            recent_activity.append({
                "timestamp": log.timestamp,
                "actionType": log.actionType,
                "userId": log.userId,
                "itemId": log.itemId,
                "summary": f"{log.actionType} - {log.details.get('reason', 'No reason')}"
            })
        
        return {
            "success": True,
            "summary": {
                "totalLogs": total_logs,
                "actionTypeCounts": action_counts,
                "userCounts": user_counts,
                "recentActivity": recent_activity
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logs summary error: {str(e)}")

@router.get("/logs/actions")
async def get_action_types():
    """
    Get list of all available action types
    """
    try:
        # Get all logs
        all_logs = storage.get_logs()
        
        # Extract unique action types
        action_types = set()
        for log in all_logs:
            action_types.add(log.actionType)
        
        return {
            "success": True,
            "actionTypes": sorted(list(action_types)),
            "descriptions": {
                "placement": "Item placement in containers",
                "retrieval": "Item retrieval from containers",
                "rearrangement": "Item movement between containers",
                "disposal": "Item marked as waste",
                "search": "Item search operations",
                "import": "Data import operations",
                "export": "Data export operations",
                "simulation": "Time simulation operations",
                "waste_identification": "Waste item identification",
                "return_plan": "Waste return planning",
                "undocking": "Container undocking operations",
                "bulk_usage": "Bulk item usage simulation",
                "simulation_reset": "Simulation time reset"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action types error: {str(e)}")

@router.get("/logs/users")
async def get_users():
    """
    Get list of all users who have performed actions
    """
    try:
        # Get all logs
        all_logs = storage.get_logs()
        
        # Extract unique users
        users = set()
        for log in all_logs:
            if log.userId:
                users.add(log.userId)
        
        # Get user activity counts
        user_activity = {}
        for log in all_logs:
            user_id = log.userId or "system"
            if user_id not in user_activity:
                user_activity[user_id] = {
                    "totalActions": 0,
                    "lastAction": None,
                    "actionTypes": set()
                }
            
            user_activity[user_id]["totalActions"] += 1
            user_activity[user_id]["actionTypes"].add(log.actionType)
            
            # Update last action if this is more recent
            if (user_activity[user_id]["lastAction"] is None or 
                log.timestamp > user_activity[user_id]["lastAction"]):
                user_activity[user_id]["lastAction"] = log.timestamp
        
        # Convert sets to lists for JSON serialization
        for user_data in user_activity.values():
            user_data["actionTypes"] = list(user_data["actionTypes"])
        
        return {
            "success": True,
            "users": sorted(list(users)),
            "userActivity": user_activity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Users error: {str(e)}")

@router.get("/logs/items/{item_id}")
async def get_item_logs(item_id: str):
    """
    Get all logs for a specific item
    """
    try:
        # Format item ID
        from backend.utils.validators import validate_item_id
        formatted_id = validate_item_id(item_id)
        
        # Get logs for this item
        logs = storage.get_logs(item_id=formatted_id)
        
        # Convert to dict format and add timeline
        log_timeline = []
        for log in logs:
            log_dict = {
                "timestamp": log.timestamp,
                "userId": log.userId,
                "actionType": log.actionType,
                "details": log.details,
                "description": _generate_log_description(log)
            }
            log_timeline.append(log_dict)
        
        return {
            "success": True,
            "itemId": formatted_id,
            "totalLogs": len(log_timeline),
            "timeline": log_timeline
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Item logs error: {str(e)}")

@router.get("/logs/performance")
async def get_performance_logs():
    """
    Get performance-related logs
    """
    try:
        # Get all logs
        all_logs = storage.get_logs()
        
        # Filter performance-related logs
        performance_logs = []
        for log in all_logs:
            if ("processing_time" in log.details or 
                "items_processed" in log.details or
                log.actionType in ["placement", "simulation", "import"]):
                
                performance_data = {
                    "timestamp": log.timestamp,
                    "actionType": log.actionType,
                    "processingTime": log.details.get("processing_time_seconds"),
                    "itemsProcessed": log.details.get("items_processed"),
                    "itemsImported": log.details.get("items_imported"),
                    "containersImported": log.details.get("containers_imported"),
                    "successfulPlacements": log.details.get("successful_placements"),
                    "details": log.details
                }
                performance_logs.append(performance_data)
        
        # Sort by timestamp (newest first)
        performance_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "success": True,
            "performanceLogs": performance_logs[:50]  # Limit to last 50
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance logs error: {str(e)}")

@router.delete("/logs/clear")
async def clear_logs():
    """
    Clear all logs (use with caution)
    """
    try:
        # Get current log count
        all_logs = storage.get_logs()
        log_count = len(all_logs)
        
        # Clear logs by creating a new empty list
        # Note: This is a simplified approach - in production you might want more sophisticated log management
        storage._logs.clear()
        
        return {
            "success": True,
            "message": f"Cleared {log_count} log entries",
            "clearedCount": log_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear logs error: {str(e)}")

def _generate_log_description(log) -> str:
    """Generate human-readable description for log entry"""
    action_type = log.actionType
    details = log.details
    
    if action_type == "placement":
        container = details.get("toContainer", "unknown container")
        return f"Item placed in {container}"
    
    elif action_type == "retrieval":
        container = details.get("fromContainer", "unknown container")
        return f"Item retrieved from {container}"
    
    elif action_type == "rearrangement":
        from_container = details.get("fromContainer", "unknown")
        to_container = details.get("toContainer", "unknown")
        return f"Item moved from {from_container} to {to_container}"
    
    elif action_type == "disposal":
        reason = details.get("reason", "unknown reason")
        return f"Item marked as waste: {reason}"
    
    elif action_type == "search":
        result = details.get("result", "unknown")
        return f"Item search: {result}"
    
    elif action_type == "import":
        import_type = details.get("import_type", "data")
        count = details.get("items_imported") or details.get("containers_imported", 0)
        return f"Imported {count} {import_type}"
    
    elif action_type == "simulation":
        days = details.get("days_simulated", "unknown")
        return f"Simulated {days} days"
    
    else:
        return f"{action_type.replace('_', ' ').title()}"
