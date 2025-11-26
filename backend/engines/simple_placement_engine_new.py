"""
Simple, fast placement algorithm for space logistics
Optimized for speed and PDF compliance
"""
from typing import List, Dict, Optional, Tuple
from backend.models.item import Item
from backend.models.container import Container

class SimplePlacementEngine:
    """Ultra-fast placement engine optimized for performance and PDF compliance"""
    
    def __init__(self):
        self.grid_step = 10.0  # 10cm grid for better performance
        
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """
        Find optimal placement for item using fast algorithm
        Returns: {containerId: str, position: dict} or None
        """
        # Get simple orientations (only 2 as per PDF - width/depth can be rotated)
        orientations = [
            (item.width, item.depth, item.height),  # Original orientation
            (item.depth, item.width, item.height)   # 90° rotation
        ]
        
        # Try preferred zone first, then other zones
        sorted_containers = self._sort_containers_by_preference(containers, item.preferredZone)
        
        for container in sorted_containers:
            container_id = container.containerId
            
            # Get existing items in this container
            existing_items_in_container = [
                placed_item for placed_item in placed_items.values()
                if hasattr(placed_item, 'containerId') and 
                placed_item.containerId == container_id and 
                hasattr(placed_item, 'position') and placed_item.position
            ]
            
            # Try each orientation
            for width, depth, height in orientations:
                # Quick bounds check
                if (width > container.width or 
                    depth > container.depth or 
                    height > container.height):
                    continue
                
                # Find position using simple algorithm
                position = self._find_simple_position(
                    width, depth, height, container, existing_items_in_container
                )
                
                if position:
                    return {
                        "containerId": container_id,
                        "position": position
                    }
        
        return None
    
    def _sort_containers_by_preference(self, containers: Dict[str, Container], 
                                     preferred_zone: str) -> List[Container]:
        """Sort containers by zone preference"""
        preferred = []
        others = []
        
        for container in containers.values():
            if container.zone == preferred_zone:
                preferred.append(container)
            else:
                others.append(container)
        
        # Sort by available space (larger containers first)
        preferred.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        others.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        
        return preferred + others
    
    def _find_simple_position(self, item_width: float, item_depth: float, item_height: float,
                           container: Container, existing_items: List[Item]) -> Optional[Dict]:
        """
        Find valid position using simple grid algorithm
        Returns position dict with startCoordinates and endCoordinates
        """
        # Try a few key positions first for speed
        test_positions = [
            (0, 0, 0),  # Bottom-left-front corner (most accessible)
            (0, 0, self.grid_step),  # Above bottom-left-front
            (self.grid_step, 0, 0),  # Right of bottom-left-front
            (0, self.grid_step, 0),  # Deeper than bottom-left-front
        ]
        
        # Add some grid positions for more thorough search
        max_grid_checks = 20  # Limit to prevent timeout
        checks = 0
        
        # Try simple positions first
        for x, y, z in test_positions:
            if checks >= max_grid_checks:
                break
            checks += 1
            
            # Ensure within bounds
            if (x + item_width <= container.width and
                y + item_depth <= container.depth and
                z + item_height <= container.height):
                
                # Check for collisions
                if self._is_position_valid(x, y, z, item_width, item_depth, 
                                         item_height, existing_items):
                    # Return position in PDF format
                    return {
                        "startCoordinates": {
                            "width": float(x),
                            "depth": float(y),
                            "height": float(z)
                        },
                        "endCoordinates": {
                            "width": float(x + item_width),
                            "depth": float(y + item_depth),
                            "height": float(z + item_height)
                        }
                    }
        
        # If simple positions don't work, try limited grid search
        w_steps = min(int((container.width - item_width) / self.grid_step) + 1, 5)
        d_steps = min(int((container.depth - item_depth) / self.grid_step) + 1, 5)
        h_steps = min(int((container.height - item_height) / self.grid_step) + 1, 5)
        
        for d_idx in range(d_steps):
            for h_idx in range(h_steps):
                for w_idx in range(w_steps):
                    if checks >= max_grid_checks:
                        break
                    checks += 1
                    
                    x = w_idx * self.grid_step
                    y = d_idx * self.grid_step  # depth (into container)
                    z = h_idx * self.grid_step  # height
                    
                    # Ensure within bounds
                    if (x + item_width <= container.width and
                        y + item_depth <= container.depth and
                        z + item_height <= container.height):
                        
                        # Check for collisions
                        if self._is_position_valid(x, y, z, item_width, item_depth, 
                                                 item_height, existing_items):
                            # Return position in PDF format
                            return {
                                "startCoordinates": {
                                    "width": float(x),
                                    "depth": float(y),
                                    "height": float(z)
                                },
                                "endCoordinates": {
                                    "width": float(x + item_width),
                                    "depth": float(y + item_depth),
                                    "height": float(z + item_height)
                                }
                            }
        
        return None
    
    def _is_position_valid(self, x: float, y: float, z: float,
                          width: float, depth: float, height: float,
                          existing_items: List[Item]) -> bool:
        """
        Check if position collides with existing items
        Uses simple bounding box collision detection
        """
        # Item bounding box
        x1, y1, z1 = x, y, z
        x2, y2, z2 = x + width, y + depth, z + height
        
        for item in existing_items:
            if not hasattr(item, 'position') or not item.position:
                continue
                
            try:
                # Existing item bounding box
                start = item.position["startCoordinates"]
                end = item.position["endCoordinates"]
                
                ex1, ey1, ez1 = start["width"], start["depth"], start["height"]
                ex2, ey2, ez2 = end["width"], end["depth"], end["height"]
                
                # Check for overlap (collision)
                if not (x2 <= ex1 or x1 >= ex2 or
                       y2 <= ey1 or y1 >= ey2 or
                       z2 <= ez1 or z1 >= ez2):
                    return False  # Collision detected
            except (KeyError, TypeError):
                # Skip items with invalid position data
                continue
        
        return True  # No collision
    
    def validate_placement(self, item: Item, container: Container, 
                          position: Dict, existing_items: Dict[str, Item]) -> Tuple[bool, str]:
        """
        Validate that a placement is valid
        Returns: (is_valid: bool, error_message: str)
        """
        try:
            start = position["startCoordinates"]
            end = position["endCoordinates"]
            
            # Check bounds
            if (start["width"] < 0 or start["depth"] < 0 or start["height"] < 0 or
                end["width"] > container.width or 
                end["depth"] > container.depth or
                end["height"] > container.height):
                return False, "Item placement out of container bounds"
            
            # Check dimensions match item
            placed_width = end["width"] - start["width"]
            placed_depth = end["depth"] - start["depth"]
            placed_height = end["height"] - start["height"]
            
            # Allow for rotations
            valid_orientations = [
                (item.width, item.depth, item.height),
                (item.depth, item.width, item.height)
            ]
            
            orientation_match = False
            for w, d, h in valid_orientations:
                if (abs(placed_width - w) < 0.1 and 
                    abs(placed_depth - d) < 0.1 and 
                    abs(placed_height - h) < 0.1):
                    orientation_match = True
                    break
            
            if not orientation_match:
                return False, f"Item dimensions don't match placement: expected {item.width}x{item.depth}x{item.height}, got {placed_width}x{placed_depth}x{placed_height}"
            
            # Check for collisions with existing items
            container_items = [
                existing_item for existing_item in existing_items.values()
                if (hasattr(existing_item, 'containerId') and 
                    existing_item.containerId == container.containerId and 
                    hasattr(existing_item, 'position') and existing_item.position)
            ]
            
            if not self._is_position_valid(
                start["width"], start["depth"], start["height"],
                placed_width, placed_depth, placed_height,
                container_items
            ):
                return False, "Item placement collides with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, items: List[Item], containers: Dict[str, Container],
                            existing_items: Dict[str, Item]) -> List[Dict]:
        """
        Suggest simple rearrangement steps
        Returns list of rearrangement operations
        """
        # For now, return empty list - rearrangement is complex
        # In real implementation, this would analyze container space and suggest moves
        return []
