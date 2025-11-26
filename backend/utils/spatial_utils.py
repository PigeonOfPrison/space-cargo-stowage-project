"""
Spatial indexing utilities for efficient collision detection
Optimized for 3D container space management
"""
from typing import List, Dict, Tuple, Optional
from backend.models.item import Item
from backend.models.container import Container

class SpatialGrid:
    """Simple spatial grid for fast collision detection"""
    
    def __init__(self, container: Container, cell_size: float = 20.0):
        """Initialize spatial grid for a container"""
        self.container = container
        self.cell_size = cell_size
        
        # Calculate grid dimensions
        self.grid_w = int(container.width / cell_size) + 1
        self.grid_d = int(container.depth / cell_size) + 1
        self.grid_h = int(container.height / cell_size) + 1
        
        # Grid to store item references
        self.grid = {}
        self.placed_items = {}
    
    def _get_cell_coords(self, x: float, y: float, z: float) -> Tuple[int, int, int]:
        """Convert world coordinates to grid cell coordinates"""
        return (
            int(x / self.cell_size),
            int(y / self.cell_size), 
            int(z / self.cell_size)
        )
    
    def _get_affected_cells(self, x: float, y: float, z: float, 
                           width: float, depth: float, height: float) -> List[Tuple[int, int, int]]:
        """Get all grid cells that an item occupies"""
        x_start, y_start, z_start = self._get_cell_coords(x, y, z)
        x_end, y_end, z_end = self._get_cell_coords(x + width, y + depth, z + height)
        
        cells = []
        for gx in range(x_start, min(x_end + 1, self.grid_w)):
            for gy in range(y_start, min(y_end + 1, self.grid_d)):
                for gz in range(z_start, min(z_end + 1, self.grid_h)):
                    cells.append((gx, gy, gz))
        return cells
    
    def add_item(self, item_id: str, x: float, y: float, z: float,
                 width: float, depth: float, height: float):
        """Add item to spatial grid"""
        # Store item bounds
        self.placed_items[item_id] = {
            'bounds': (x, y, z, x + width, y + depth, z + height)
        }
        
        # Add to grid cells
        cells = self._get_affected_cells(x, y, z, width, depth, height)
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(item_id)
    
    def check_collision(self, x: float, y: float, z: float,
                       width: float, depth: float, height: float) -> bool:
        """Fast collision check using spatial grid"""
        # Get potentially colliding cells
        cells = self._get_affected_cells(x, y, z, width, depth, height)
        
        # Check each cell for collisions
        item_bounds = (x, y, z, x + width, y + depth, z + height)
        
        for cell in cells:
            if cell in self.grid:
                for item_id in self.grid[cell]:
                    existing_bounds = self.placed_items[item_id]['bounds']
                    if self._bounds_overlap(item_bounds, existing_bounds):
                        return True
        return False
    
    def _bounds_overlap(self, bounds1: Tuple[float, float, float, float, float, float],
                       bounds2: Tuple[float, float, float, float, float, float]) -> bool:
        """Check if two 3D bounding boxes overlap"""
        x1_min, y1_min, z1_min, x1_max, y1_max, z1_max = bounds1
        x2_min, y2_min, z2_min, x2_max, y2_max, z2_max = bounds2
        
        return not (x1_max <= x2_min or x1_min >= x2_max or
                   y1_max <= y2_min or y1_min >= y2_max or
                   z1_max <= z2_min or z1_min >= z2_max)

class AccessibilityCalculator:
    """Calculate accessibility scores for retrieval optimization"""
    
    @staticmethod
    def calculate_retrieval_steps(item_position: Dict, container: Container, 
                                 placed_items: List[Item]) -> int:
        """
        Calculate retrieval steps needed based on PDF definition
        Items can only be moved perpendicular to open face (depth direction)
        """
        if not item_position:
            return float('inf')
        
        start_coords = item_position["startCoordinates"]
        end_coords = item_position["endCoordinates"]
        
        item_depth_start = start_coords["depth"]
        item_depth_end = end_coords["depth"]
        item_width_start = start_coords["width"]
        item_width_end = end_coords["width"]
        item_height_start = start_coords["height"]
        item_height_end = end_coords["height"]
        
        steps = 0
        
        # Check for blocking items in the path to opening (depth = 0)
        for other_item in placed_items:
            if not hasattr(other_item, 'position') or not other_item.position:
                continue
                
            other_start = other_item.position["startCoordinates"]
            other_end = other_item.position["endCoordinates"]
            
            # Check if other item blocks the path to opening
            if (other_start["depth"] < item_depth_start and  # Other item is closer to opening
                other_end["depth"] > item_depth_start and    # And extends past our start
                # And overlaps in width and height
                not (item_width_end <= other_start["width"] or item_width_start >= other_end["width"] or
                     item_height_end <= other_start["height"] or item_height_start >= other_end["height"])):
                steps += 1
        
        return steps
    
    @staticmethod
    def calculate_accessibility_score(x: float, y: float, z: float, 
                                    container: Container, priority: int) -> float:
        """
        Calculate accessibility score for position
        Higher score = better accessibility for high priority items
        """
        # Prefer positions near opening (low depth)
        depth_score = 1.0 - (y / container.depth)
        
        # Prefer lower heights for easier access
        height_score = 1.0 - (z / container.height) * 0.3
        
        # Priority bonus for accessible positions
        priority_bonus = (priority / 100.0) * depth_score
        
        return depth_score + height_score + priority_bonus
