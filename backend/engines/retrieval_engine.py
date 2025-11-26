from typing import List, Dict, Optional, Tuple
from backend.models.item import Item
from backend.models.container import Container
from backend.utils.coordinates import Coordinates3D, BoundingBox

class RetrievalEngine:
    """Handles item retrieval optimization and step calculation"""
    
    def __init__(self):
        self.epsilon = 1e-5
    
    def find_item_by_id(self, item_id: str, placed_items: Dict[str, Item]) -> Optional[Item]:
        """Find item by ID"""
        return placed_items.get(item_id)
    
    def find_items_by_name(self, item_name: str, placed_items: Dict[str, Item]) -> List[Item]:
        """Find items by name"""
        matches = []
        for item in placed_items.values():
            if item.name.lower() == item_name.lower():
                matches.append(item)
        return matches
    
    def find_best_item_to_retrieve(self, item_name: str, placed_items: Dict[str, Item], 
                                 containers: Dict[str, Container]) -> Optional[Item]:
        """Find the best item to retrieve based on accessibility and expiry"""
        candidates = self.find_items_by_name(item_name, placed_items)
        
        if not candidates:
            return None
        
        # If only one item, return it
        if len(candidates) == 1:
            return candidates[0]
        
        # Score each candidate
        best_item = None
        best_score = float('-inf')
        
        for item in candidates:
            if not item.containerId or not item.position:
                continue
                
            container = containers.get(item.containerId)
            if not container:
                continue
            
            # Calculate retrieval steps
            steps_needed = self.calculate_retrieval_steps(item, placed_items, containers)
            
            # Calculate score (lower steps = higher score)
            score = 100 - steps_needed
            
            # Prefer items closer to expiry
            if item.expiryDate and item.expiryDate != "N/A":
                try:
                    from datetime import datetime
                    expiry = datetime.fromisoformat(item.expiryDate)
                    now = datetime.now()
                    days_to_expiry = (expiry - now).days
                    
                    if days_to_expiry < 30:  # Expiring soon
                        score += 20
                    elif days_to_expiry < 7:  # Expiring very soon
                        score += 50
                except:
                    pass
            
            # Prefer items with fewer remaining uses
            usage_ratio = item.currentUses / item.usageLimit
            if usage_ratio > 0.8:  # Almost depleted
                score += 15
            
            if score > best_score:
                best_score = score
                best_item = item
        
        return best_item
    
    def calculate_retrieval_steps(self, target_item: Item, placed_items: Dict[str, Item], 
                                containers: Dict[str, Container]) -> int:
        """Calculate number of steps needed to retrieve an item"""
        if not target_item.containerId or not target_item.position:
            return 0
        
        container = containers.get(target_item.containerId)
        if not container:
            return 0
        
        # Get target item's bounding box
        target_start = Coordinates3D.from_dict(target_item.position["startCoordinates"])
        target_end = Coordinates3D.from_dict(target_item.position["endCoordinates"])
        target_box = BoundingBox(target_start, target_end)
        
        # Find items that block the retrieval path
        blocking_items = []
        
        for item in placed_items.values():
            if (item.containerId == target_item.containerId and 
                item.itemId != target_item.itemId and 
                item.position):
                
                item_start = Coordinates3D.from_dict(item.position["startCoordinates"])
                item_end = Coordinates3D.from_dict(item.position["endCoordinates"])
                
                # Check if item blocks the retrieval path
                # An item blocks if it's in front (smaller depth) and overlaps in width/height
                if (item_end.depth > target_start.depth and  # Item is in front
                    self._overlaps_in_plane(target_start, target_end, item_start, item_end)):
                    blocking_items.append(item)
        
        # Sort blocking items by depth (closest to opening first)
        blocking_items.sort(key=lambda x: 
            Coordinates3D.from_dict(x.position["startCoordinates"]).depth)
        
        return len(blocking_items)
    
    def _overlaps_in_plane(self, target_start: Coordinates3D, target_end: Coordinates3D,
                          item_start: Coordinates3D, item_end: Coordinates3D) -> bool:
        """Check if two items overlap in the width-height plane"""
        width_overlap = not (target_end.width <= item_start.width or 
                           target_start.width >= item_end.width)
        height_overlap = not (target_end.height <= item_start.height or 
                            target_start.height >= item_end.height)
        
        return width_overlap and height_overlap
    
    def get_retrieval_steps(self, target_item: Item, placed_items: Dict[str, Item], 
                          containers: Dict[str, Container]) -> List[Dict]:
        """Get detailed retrieval steps"""
        steps = []
        step_number = 1
        
        if not target_item.containerId or not target_item.position:
            return steps
        
        # Get items that need to be moved
        blocking_items = self._get_blocking_items(target_item, placed_items, containers)
        
        # Add steps to remove blocking items
        for item in blocking_items:
            steps.append({
                "step": step_number,
                "action": "remove",
                "itemId": item.itemId,
                "itemName": item.name
            })
            step_number += 1
        
        # Add step to retrieve target item
        steps.append({
            "step": step_number,
            "action": "retrieve",
            "itemId": target_item.itemId,
            "itemName": target_item.name
        })
        step_number += 1
        
        # Add steps to place back blocking items (in reverse order)
        for item in reversed(blocking_items):
            steps.append({
                "step": step_number,
                "action": "placeBack",
                "itemId": item.itemId,
                "itemName": item.name
            })
            step_number += 1
        
        return steps
    
    def _get_blocking_items(self, target_item: Item, placed_items: Dict[str, Item], 
                          containers: Dict[str, Container]) -> List[Item]:
        """Get list of items that block the target item's retrieval"""
        if not target_item.containerId or not target_item.position:
            return []
        
        target_start = Coordinates3D.from_dict(target_item.position["startCoordinates"])
        target_end = Coordinates3D.from_dict(target_item.position["endCoordinates"])
        
        blocking_items = []
        
        for item in placed_items.values():
            if (item.containerId == target_item.containerId and 
                item.itemId != target_item.itemId and 
                item.position):
                
                item_start = Coordinates3D.from_dict(item.position["startCoordinates"])
                item_end = Coordinates3D.from_dict(item.position["endCoordinates"])
                
                # Check if item blocks the retrieval path
                if (item_end.depth > target_start.depth and  # Item is in front
                    self._overlaps_in_plane(target_start, target_end, item_start, item_end)):
                    blocking_items.append(item)
        
        # Sort by depth (closest to opening first)
        blocking_items.sort(key=lambda x: 
            Coordinates3D.from_dict(x.position["startCoordinates"]).depth)
        
        return blocking_items
    
    def simulate_retrieval(self, item_id: str, user_id: str, placed_items: Dict[str, Item], 
                         containers: Dict[str, Container]) -> Tuple[bool, str, Optional[Item]]:
        """Simulate item retrieval and update usage count"""
        item = placed_items.get(item_id)
        
        if not item:
            return False, f"Item {item_id} not found", None
        
        if not item.containerId or not item.position:
            return False, f"Item {item_id} is not placed in any container", None
        
        # Check if item is still usable
        from datetime import datetime
        current_date = datetime.now()
        
        if item.is_expired(current_date):
            return False, f"Item {item_id} is expired", None
        
        if item.is_depleted():
            return False, f"Item {item_id} has no remaining uses", None
        
        # Increment usage count
        item.currentUses += 1
        
        # If item is now depleted, mark for waste management
        if item.is_depleted():
            # Keep item in place but mark as waste
            pass
        
        return True, "Item retrieved successfully", item
