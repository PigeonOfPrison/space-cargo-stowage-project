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
        """Sort containers using flexible zone matching utility"""
        preferred = []
        similar = []
        others = []
        
        for container in containers.values():
            match_score = PlacementUtils.zones_match(preferred_zone, container.zone)
            
            if match_score == 2:  # Exact match
                preferred.append(container)
            elif match_score == 1:  # Partial match
                similar.append(container)
            else:  # No match
                others.append(container)
        
        # Sort each group by available space
        for group in [preferred, similar, others]:
            group.sort(key=lambda c: c.width * c.depth * c.height, reverse=True)
        
        return preferred + similar + others
    
    def _populate_grid_with_existing_items(self, container_id: str, placed_items: Dict[str, Item]):
        """Populate spatial grid with existing items in container"""
        grid = self.container_grids[container_id]
        
        for item in placed_items.values():
            if (hasattr(item, 'containerId') and item.containerId == container_id and
                hasattr(item, 'position') and item.position):
                
                start = item.position["startCoordinates"]
                end = item.position["endCoordinates"]
                
                grid.add_item(
                    item.itemId,
                    start["width"], start["depth"], start["height"],
                    end["width"] - start["width"],
                    end["depth"] - start["depth"],
                    end["height"] - start["height"]
                )
    
    def _find_position_with_utilities(self, width: float, depth: float, height: float,
                                    container: Container, priority: int) -> Optional[Dict]:
        """Find position using modular utilities"""
        # Get candidate positions using utility
        positions = PlacementUtils.find_best_positions(
            container, width, depth, height, max_positions=15
        )
        
        grid = self.container_grids[container.containerId]
        best_position = None
        best_score = -1
        
        for x, y, z in positions:
            # Check collision using spatial grid
            if not grid.check_collision(x, y, z, width, depth, height):
                # Calculate accessibility score
                score = AccessibilityCalculator.calculate_accessibility_score(
                    x, y, z, container, priority
                )
                
                if score > best_score:
                    best_score = score
                    best_position = PlacementUtils.create_position_dict(
                        x, y, z, width, depth, height
                    )
        
        return best_position
    
    def validate_placement(self, item: Item, container: Container, 
                          position: Dict, existing_items: Dict[str, Item]) -> Tuple[bool, str]:
        """
        Validate placement using utilities
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
            
            # Check dimensions using utility
            placed_width = end["width"] - start["width"]
            placed_depth = end["depth"] - start["depth"]
            placed_height = end["height"] - start["height"]
            
            valid_orientations = PlacementUtils.get_item_orientations(item)
            orientation_match = any(
                abs(placed_width - w) < 0.1 and 
                abs(placed_depth - d) < 0.1 and 
                abs(placed_height - h) < 0.1
                for w, d, h in valid_orientations
            )
            
            if not orientation_match:
                return False, f"Invalid dimensions: {placed_width}x{placed_depth}x{placed_height}"
            
            # Check collisions using spatial grid
            if container.containerId in self.container_grids:
                grid = self.container_grids[container.containerId]
                if grid.check_collision(
                    start["width"], start["depth"], start["height"],
                    placed_width, placed_depth, placed_height
                ):
                    return False, "Collision with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, items: List[Item], containers: Dict[str, Container],
                            existing_items: Dict[str, Item]) -> List[Dict]:
        """
        Suggest simple rearrangement steps
        Returns list of rearrangement operations
        """
        # For now, return empty list - complex rearrangement logic would go here
        return []
