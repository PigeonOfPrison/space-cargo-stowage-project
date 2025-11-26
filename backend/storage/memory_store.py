from typing import Dict, List, Optional
from backend.models.item import Item
from backend.models.container import Container
from backend.models.log_entry import LogEntry
from datetime import datetime
import threading

class MemoryStore:
    """In-memory storage system for the application"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._items: Dict[str, Item] = {}
        self._containers: Dict[str, Container] = {}
        self._logs: List[LogEntry] = []
        self._simulation_date = datetime.now()
    
    # Item operations
    def add_item(self, item: Item) -> bool:
        """Add an item to storage"""
        with self._lock:
            if item.itemId in self._items:
                return False  # Item already exists
            self._items[item.itemId] = item
            return True
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by ID"""
        with self._lock:
            return self._items.get(item_id)
    
    def update_item(self, item: Item) -> bool:
        """Update an existing item"""
        with self._lock:
            if item.itemId not in self._items:
                return False
            self._items[item.itemId] = item
            return True
    
    def remove_item(self, item_id: str) -> bool:
        """Remove an item from storage"""
        with self._lock:
            if item_id in self._items:
                del self._items[item_id]
                return True
            return False
    
    def get_all_items(self) -> Dict[str, Item]:
        """Get all items"""
        with self._lock:
            return self._items.copy()
    
    def add_multiple_items(self, items: List[Item]) -> int:
        """Add multiple items and return count of successful additions"""
        with self._lock:
            added_count = 0
            for item in items:
                if item.itemId not in self._items:
                    self._items[item.itemId] = item
                    added_count += 1
            return added_count
    
    # Container operations
    def add_container(self, container: Container) -> bool:
        """Add a container to storage"""
        with self._lock:
            if container.containerId in self._containers:
                return False  # Container already exists
            self._containers[container.containerId] = container
            return True
    
    def get_container(self, container_id: str) -> Optional[Container]:
        """Get a container by ID"""
        with self._lock:
            return self._containers.get(container_id)
    
    def update_container(self, container: Container) -> bool:
        """Update an existing container"""
        with self._lock:
            if container.containerId not in self._containers:
                return False
            self._containers[container.containerId] = container
            return True
    
    def remove_container(self, container_id: str) -> bool:
        """Remove a container from storage"""
        with self._lock:
            if container_id in self._containers:
                del self._containers[container_id]
                return True
            return False
    
    def get_all_containers(self) -> Dict[str, Container]:
        """Get all containers"""
        with self._lock:
            return self._containers.copy()
    
    def add_multiple_containers(self, containers: List[Container]) -> int:
        """Add multiple containers and return count of successful additions"""
        with self._lock:
            added_count = 0
            for container in containers:
                if container.containerId not in self._containers:
                    self._containers[container.containerId] = container
                    added_count += 1
            return added_count
    
    def get_containers_by_zone(self, zone: str) -> Dict[str, Container]:
        """Get all containers in a specific zone"""
        with self._lock:
            return {cid: container for cid, container in self._containers.items() 
                   if container.zone == zone}
    
    # Log operations
    def add_log(self, log_entry: LogEntry) -> None:
        """Add a log entry"""
        with self._lock:
            self._logs.append(log_entry)
    
    def get_logs(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                item_id: Optional[str] = None, user_id: Optional[str] = None,
                action_type: Optional[str] = None) -> List[LogEntry]:
        """Get logs with optional filtering"""
        with self._lock:
            filtered_logs = self._logs.copy()
        
        # Apply filters
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                filtered_logs = [log for log in filtered_logs 
                               if datetime.fromisoformat(log.timestamp) >= start_dt]
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                filtered_logs = [log for log in filtered_logs 
                               if datetime.fromisoformat(log.timestamp) <= end_dt]
            except ValueError:
                pass
        
        if item_id:
            filtered_logs = [log for log in filtered_logs if log.itemId == item_id]
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.userId == user_id]
        
        if action_type:
            filtered_logs = [log for log in filtered_logs if log.actionType == action_type]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_logs
    
    # Simulation date operations
    def set_simulation_date(self, date: datetime) -> None:
        """Set current simulation date"""
        with self._lock:
            self._simulation_date = date
    
    def get_simulation_date(self) -> datetime:
        """Get current simulation date"""
        with self._lock:
            return self._simulation_date
    
    # Utility operations
    def clear_all_data(self) -> None:
        """Clear all data (useful for testing)"""
        with self._lock:
            self._items.clear()
            self._containers.clear()
            self._logs.clear()
            self._simulation_date = datetime.now()
    
    def clear(self) -> bool:
        """Clear all data and return success status"""
        try:
            with self._lock:
                self._items.clear()
                self._containers.clear()
                self._logs.clear()
                self._simulation_date = datetime.now()
                return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        with self._lock:
            placed_items = sum(1 for item in self._items.values() if item.containerId)
            unplaced_items = len(self._items) - placed_items
            
            container_utilization = {}
            for container_id, container in self._containers.items():
                used_volume = container.get_used_volume(self._items)
                total_volume = container.get_volume()
                utilization = (used_volume / total_volume * 100) if total_volume > 0 else 0
                container_utilization[container_id] = {
                    "utilization_percent": round(utilization, 2),
                    "used_volume": round(used_volume, 2),
                    "total_volume": round(total_volume, 2)
                }
            
            return {
                "total_items": len(self._items),
                "placed_items": placed_items,
                "unplaced_items": unplaced_items,
                "total_containers": len(self._containers),
                "total_logs": len(self._logs),
                "simulation_date": self._simulation_date.isoformat(),
                "container_utilization": container_utilization
            }
    
    def backup_data(self) -> Dict:
        """Create a backup of all data"""
        with self._lock:
            return {
                "items": {item_id: item.dict() for item_id, item in self._items.items()},
                "containers": {cid: container.dict() for cid, container in self._containers.items()},
                "logs": [log.dict() for log in self._logs],
                "simulation_date": self._simulation_date.isoformat()
            }
    
    def restore_data(self, backup_data: Dict) -> bool:
        """Restore data from backup"""
        try:
            with self._lock:
                # Clear existing data
                self._items.clear()
                self._containers.clear()
                self._logs.clear()
                
                # Restore items
                for item_id, item_data in backup_data.get("items", {}).items():
                    self._items[item_id] = Item(**item_data)
                
                # Restore containers
                for container_id, container_data in backup_data.get("containers", {}).items():
                    self._containers[container_id] = Container(**container_data)
                
                # Restore logs
                for log_data in backup_data.get("logs", []):
                    self._logs.append(LogEntry(**log_data))
                
                # Restore simulation date
                if "simulation_date" in backup_data:
                    self._simulation_date = datetime.fromisoformat(backup_data["simulation_date"])
                
                return True
        except Exception as e:
            print(f"Error restoring data: {e}")
            return False

# Global storage instance
storage = MemoryStore()
