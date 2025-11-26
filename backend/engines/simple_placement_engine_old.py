"""
Simple, fast placement algorithm for space logistics
Modular design with utilities - optimized for PDF compliance
"""
from typing import List, Dict, Optional, Tuple
from backend.models.item import Item
from backend.models.container import Container
from backend.utils.placement_utils import PlacementUtils
from backend.utils.spatial_utils import SpatialGrid, AccessibilityCalculator

class SimplePlacementEngine:
    """Fast placement engine using modular utilities for PDF compliance"""
    
    def __init__(self):
        # Cache spatial grids for better performance
        self.container_grids: Dict[str, SpatialGrid] = {}
        
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """
        Find optimal placement using modular utilities
        Returns: {containerId: str, position: dict} or None
        """
        # Get valid orientations using utility
        orientations = PlacementUtils.get_item_orientations(item)
        
        # Sort containers by preference
        sorted_containers = self._sort_containers_by_preference(containers, item.preferredZone)
        
        for container in sorted_containers:
            container_id = container.containerId
            
            # Initialize spatial grid if needed
            if container_id not in self.container_grids:
                self.container_grids[container_id] = SpatialGrid(container)
                self._populate_grid_with_existing_items(container_id, placed_items)
            
            # Try each orientation
            for width, depth, height in orientations:
                if not PlacementUtils.fits_in_container(width, depth, height, container):
                    continue
                
                # Find position using utilities
                position = self._find_position_with_utilities(
                    width, depth, height, container, item.priority
                )
                
                if position:
                    # Update spatial grid
                    start = position["startCoordinates"]
                    self.container_grids[container_id].add_item(
                        item.itemId, start["width"], start["depth"], start["height"],
                        width, depth, height
                    )
                    
                    return {
                        "containerId": container_id,
                        "position": position
                    }
        
        return None
    
    def _sort_containers_by_preference(self, containers: Dict[str, Container], 
                                     preferred_zone: str) -> List[Container]:
        """Sort containers by zone preference - more flexible zone matching"""
        preferred = []
        similar = []
        others = []
        
        for container in containers.values():
            container_zone = container.zone.lower().replace('_', '').replace(' ', '')
            preferred_zone_clean = preferred_zone.lower().replace('_', '').replace(' ', '')
            
            if container_zone == preferred_zone_clean:
                # Exact match
                preferred.append(container)
            elif (container_zone in preferred_zone_clean or 
                  preferred_zone_clean in container_zone or
                  any(word in container_zone for word in preferred_zone_clean.split()) or
                  any(word in preferred_zone_clean for word in container_zone.split())):
                # Partial match (e.g., "storage" matches "storage_bay")
                similar.append(container)
            else:
                others.append(container)
        
        # Sort each group by available space (larger containers first)
        preferred.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        similar.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        others.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        
        return preferred + similar + others
    
    def _find_simple_position(self, item_width: float, item_depth: float, item_height: float,
                           container: Container, existing_items: List[Item]) -> Optional[Dict]:
        """
        Find valid position using simple algorithm with more thorough search
        Returns position dict with startCoordinates and endCoordinates
        """
        # Try simple positions first for speed
        test_positions = [
            (0, 0, 0),  # Bottom-left-front corner (most accessible)
            (0, 0, self.grid_step),  # Above bottom-left-front
            (self.grid_step, 0, 0),  # Right of bottom-left-front
            (0, self.grid_step, 0),  # Deeper than bottom-left-front
        ]
        
        # Try simple positions first
        for x, y, z in test_positions:
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
        
        # If simple positions don't work, try more comprehensive grid search
        max_grid_checks = 100  # Increased for better placement rate
        checks = 0
        
        # Create a more thorough grid search
        step_w = min(self.grid_step, container.width / 10)
        step_d = min(self.grid_step, container.depth / 10) 
        step_h = min(self.grid_step, container.height / 10)
        
        w_steps = min(int((container.width - item_width) / step_w) + 1, 10)
        d_steps = min(int((container.depth - item_depth) / step_d) + 1, 10)
        h_steps = min(int((container.height - item_height) / step_h) + 1, 10)
        
        # Try accessible positions first (low depth), then work inward
        for d_idx in range(d_steps):
            for h_idx in range(h_steps):
                for w_idx in range(w_steps):
                    if checks >= max_grid_checks:
                        break
                    checks += 1
                    
                    x = w_idx * step_w
                    y = d_idx * step_d  # depth (into container)
                    z = h_idx * step_h  # height
                    
                    # Ensure within bounds with some tolerance
                    if (x + item_width <= container.width + 0.1 and
                        y + item_depth <= container.depth + 0.1 and
                        z + item_height <= container.height + 0.1):
                        
                        # Adjust if slightly over bounds
                        if x + item_width > container.width:
                            x = container.width - item_width
                        if y + item_depth > container.depth:
                            y = container.depth - item_depth
                        if z + item_height > container.height:
                            z = container.height - item_height
                            
                        # Final bounds check
                        if x >= 0 and y >= 0 and z >= 0:
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
