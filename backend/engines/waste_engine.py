from typing import List, Dict, Optional, Tuple
from datetime import datetime
from backend.models.item import Item, ItemStatus
from backend.models.container import Container
from backend.engines.retrieval_engine import RetrievalEngine

class WasteEngine:
    """Handles waste identification, tracking, and return planning"""
    
    def __init__(self):
        self.retrieval_engine = RetrievalEngine()
    
    def identify_waste_items(self, placed_items: Dict[str, Item], 
                           current_date: Optional[datetime] = None) -> List[Dict]:
        """Identify items that are waste (expired or depleted)"""
        if current_date is None:
            current_date = datetime.now()
        
        waste_items = []
        
        for item in placed_items.values():
            if not item.containerId or not item.position:
                continue
                
            reason = None
            
            if item.is_expired(current_date):
                reason = "Expired"
            elif item.is_depleted():
                reason = "Out of Uses"
            
            if reason:
                waste_items.append({
                    "itemId": item.itemId,
                    "name": item.name,
                    "reason": reason,
                    "containerId": item.containerId,
                    "position": item.position
                })
        
        return waste_items
    
    def calculate_return_plan(self, undocking_container_id: str, max_weight: float,
                            placed_items: Dict[str, Item], containers: Dict[str, Container],
                            current_date: Optional[datetime] = None) -> Dict:
        """Calculate optimal return plan for waste items"""
        if current_date is None:
            current_date = datetime.now()
        
        # Get all waste items
        waste_items = self.identify_waste_items(placed_items, current_date)
        
        if not waste_items:
            return {
                "returnPlan": [],
                "retrievalSteps": [],
                "returnManifest": {
                    "undockingContainerId": undocking_container_id,
                    "undockingDate": current_date.isoformat(),
                    "returnItems": [],
                    "totalVolume": 0.0,
                    "totalWeight": 0.0
                }
            }
        
        # Check if undocking container exists
        undocking_container = containers.get(undocking_container_id)
        if not undocking_container:
            raise ValueError(f"Undocking container {undocking_container_id} not found")
        
        # Sort waste items by priority (retrieve high-value waste first)
        # and by retrieval difficulty (easier to retrieve first)
        prioritized_waste = []
        
        for waste_item_info in waste_items:
            item = placed_items[waste_item_info["itemId"]]
            retrieval_steps = self.retrieval_engine.calculate_retrieval_steps(
                item, placed_items, containers
            )
            
            # Calculate priority score (lower is better for waste removal)
            priority_score = retrieval_steps - item.priority * 0.1  # Easier retrieval and higher priority items first
            
            prioritized_waste.append({
                "item": item,
                "waste_info": waste_item_info,
                "retrieval_steps": retrieval_steps,
                "priority_score": priority_score
            })
        
        prioritized_waste.sort(key=lambda x: x["priority_score"])
        
        # Plan which items to return based on weight constraint
        return_plan = []
        return_items = []
        total_weight = 0.0
        total_volume = 0.0
        step_counter = 1
        
        # Available volume in undocking container
        available_volume = undocking_container.get_available_volume(placed_items)
        
        for waste_data in prioritized_waste:
            item = waste_data["item"]
            
            # Check weight constraint
            if total_weight + item.mass > max_weight:
                continue
            
            # Check volume constraint
            item_volume = item.get_volume()
            if total_volume + item_volume > available_volume:
                continue
            
            # Add to return plan
            return_plan.append({
                "step": step_counter,
                "itemId": item.itemId,
                "itemName": item.name,
                "fromContainer": item.containerId,
                "toContainer": undocking_container_id
            })
            
            return_items.append({
                "itemId": item.itemId,
                "name": item.name,
                "reason": waste_data["waste_info"]["reason"]
            })
            
            total_weight += item.mass
            total_volume += item_volume
            step_counter += 1
        
        # Generate detailed retrieval steps for all items in return plan
        all_retrieval_steps = []
        retrieval_step_counter = 1
        
        for plan_item in return_plan:
            item = placed_items[plan_item["itemId"]]
            item_retrieval_steps = self.retrieval_engine.get_retrieval_steps(
                item, placed_items, containers
            )
            
            # Renumber steps to be sequential
            for step in item_retrieval_steps:
                step["step"] = retrieval_step_counter
                all_retrieval_steps.append(step)
                retrieval_step_counter += 1
        
        return {
            "returnPlan": return_plan,
            "retrievalSteps": all_retrieval_steps,
            "returnManifest": {
                "undockingContainerId": undocking_container_id,
                "undockingDate": current_date.isoformat(),
                "returnItems": return_items,
                "totalVolume": total_volume,
                "totalWeight": total_weight
            }
        }
    
    def execute_undocking(self, undocking_container_id: str, placed_items: Dict[str, Item],
                         containers: Dict[str, Container]) -> Tuple[bool, int]:
        """Execute undocking process - remove container and all its items"""
        
        if undocking_container_id not in containers:
            return False, 0
        
        # Count items to be removed
        items_removed = 0
        items_to_remove = []
        
        for item_id, item in placed_items.items():
            if item.containerId == undocking_container_id:
                items_to_remove.append(item_id)
                items_removed += 1
        
        # Remove items from storage
        for item_id in items_to_remove:
            if item_id in placed_items:
                del placed_items[item_id]
        
        # Remove container
        if undocking_container_id in containers:
            del containers[undocking_container_id]
        
        return True, items_removed
    
    def get_waste_statistics(self, placed_items: Dict[str, Item], 
                           current_date: Optional[datetime] = None) -> Dict:
        """Get waste statistics for reporting"""
        if current_date is None:
            current_date = datetime.now()
        
        waste_items = self.identify_waste_items(placed_items, current_date)
        
        stats = {
            "totalWasteItems": len(waste_items),
            "wasteByReason": {"Expired": 0, "Out of Uses": 0},
            "wasteByZone": {},
            "totalWasteVolume": 0.0,
            "totalWasteMass": 0.0
        }
        
        for waste_item_info in waste_items:
            item = placed_items[waste_item_info["itemId"]]
            
            # Count by reason
            reason = waste_item_info["reason"]
            if reason in stats["wasteByReason"]:
                stats["wasteByReason"][reason] += 1
            
            # Count by zone
            container_id = item.containerId
            if container_id:
                # We'd need container info to get zone, simplified for now
                zone = waste_item_info.get("zone", "Unknown")
                if zone not in stats["wasteByZone"]:
                    stats["wasteByZone"][zone] = 0
                stats["wasteByZone"][zone] += 1
            
            # Add to totals
            stats["totalWasteVolume"] += item.get_volume()
            stats["totalWasteMass"] += item.mass
        
        return stats
    
    def suggest_waste_consolidation(self, placed_items: Dict[str, Item], 
                                  containers: Dict[str, Container],
                                  target_container_id: str) -> List[Dict]:
        """Suggest moving all waste items to a target container for easier undocking"""
        waste_items = self.identify_waste_items(placed_items)
        
        if not waste_items:
            return []
        
        target_container = containers.get(target_container_id)
        if not target_container:
            return []
        
        consolidation_plan = []
        step_counter = 1
        available_volume = target_container.get_available_volume(placed_items)
        used_volume = 0.0
        
        for waste_item_info in waste_items:
            item = placed_items[waste_item_info["itemId"]]
            item_volume = item.get_volume()
            
            # Check if item can fit
            if used_volume + item_volume <= available_volume:
                if item.containerId != target_container_id:  # Only move if not already there
                    consolidation_plan.append({
                        "step": step_counter,
                        "action": "move",
                        "itemId": item.itemId,
                        "fromContainer": item.containerId,
                        "toContainer": target_container_id
                    })
                    step_counter += 1
                    used_volume += item_volume
        
        return consolidation_plan
