"""
Space Optimizer - Advanced 3D space packing algorithms
"""
from typing import List, Tuple, Dict, Optional, Set
import math
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Space3D:
    """3D space representation with enhanced operations"""
    x: float
    y: float
    z: float
    width: float
    depth: float
    height: float
    
    @property
    def volume(self) -> float:
        return self.width * self.depth * self.height
    
    @property
    def bottom_left_front(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    @property
    def top_right_back(self) -> Tuple[float, float, float]:
        return (self.x + self.width, self.y + self.depth, self.z + self.height)
    
    def contains_point(self, x: float, y: float, z: float) -> bool:
        """Check if a point is inside this space"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.depth and
                self.z <= z <= self.z + self.height)
    
    def intersects(self, other: 'Space3D') -> bool:
        """Check if this space intersects with another"""
        return not (self.x + self.width <= other.x or
                   other.x + other.width <= self.x or
                   self.y + self.depth <= other.y or
                   other.y + other.depth <= self.y or
                   self.z + self.height <= other.z or
                   other.z + other.height <= self.z)
    
    def can_fit(self, width: float, depth: float, height: float) -> bool:
        """Check if dimensions can fit in this space"""
        return (self.width >= width and 
                self.depth >= depth and 
                self.height >= height)

class SpaceOptimizer:
    """Advanced 3D space optimization using multiple algorithms"""
    
    def __init__(self):
        self.space_cache = {}
        
    def find_best_fit_position(self, available_spaces: List[Space3D], 
                              item_dims: Tuple[float, float, float],
                              strategy: str = "best_fit") -> Optional[Tuple[Space3D, Tuple[float, float, float]]]:
        """
        Find the best position using various placement strategies
        """
        width, depth, height = item_dims
        
        # Filter spaces that can fit the item
        fitting_spaces = [space for space in available_spaces 
                         if space.can_fit(width, depth, height)]
        
        if not fitting_spaces:
            return None
        
        if strategy == "best_fit":
            return self._best_fit_strategy(fitting_spaces, item_dims)
        elif strategy == "bottom_left":
            return self._bottom_left_strategy(fitting_spaces, item_dims)
        elif strategy == "corner_fit":
            return self._corner_fit_strategy(fitting_spaces, item_dims)
        elif strategy == "skyline":
            return self._skyline_strategy(fitting_spaces, item_dims)
        else:
            return self._best_fit_strategy(fitting_spaces, item_dims)
    
    def _best_fit_strategy(self, spaces: List[Space3D], 
                          item_dims: Tuple[float, float, float]) -> Optional[Tuple[Space3D, Tuple[float, float, float]]]:
        """Find space with minimum waste volume"""
        width, depth, height = item_dims
        
        best_space = None
        min_waste = float('inf')
        
        for space in spaces:
            waste = space.volume - (width * depth * height)
            if waste < min_waste:
                min_waste = waste
                best_space = space
        
        if best_space:
            return (best_space, (best_space.x, best_space.y, best_space.z))
        return None
    
    def _bottom_left_strategy(self, spaces: List[Space3D], 
                             item_dims: Tuple[float, float, float]) -> Optional[Tuple[Space3D, Tuple[float, float, float]]]:
        """Place item at lowest, leftmost, frontmost position"""
        width, depth, height = item_dims
        
        # Sort by z (height), then y (depth), then x (width)
        sorted_spaces = sorted(spaces, key=lambda s: (s.z, s.y, s.x))
        
        for space in sorted_spaces:
            if space.can_fit(width, depth, height):
                return (space, (space.x, space.y, space.z))
        
        return None
    
    def _corner_fit_strategy(self, spaces: List[Space3D], 
                            item_dims: Tuple[float, float, float]) -> Optional[Tuple[Space3D, Tuple[float, float, float]]]:
        """Prefer positions that touch multiple container walls/items"""
        width, depth, height = item_dims
        
        scored_spaces = []
        for space in spaces:
            if space.can_fit(width, depth, height):
                # Score based on how many walls/corners the item would touch
                corner_score = 0
                
                # Check proximity to container edges (assuming container starts at 0,0,0)
                if space.x == 0:  # Left wall
                    corner_score += 2
                if space.y == 0:  # Front wall
                    corner_score += 2
                if space.z == 0:  # Bottom
                    corner_score += 3  # Bottom contact is most important for stability
                
                scored_spaces.append((corner_score, space))
        
        if scored_spaces:
            # Sort by score (higher is better)
            scored_spaces.sort(reverse=True)
            best_space = scored_spaces[0][1]
            return (best_space, (best_space.x, best_space.y, best_space.z))
        
        return None
    
    def _skyline_strategy(self, spaces: List[Space3D], 
                         item_dims: Tuple[float, float, float]) -> Optional[Tuple[Space3D, Tuple[float, float, float]]]:
        """Use skyline algorithm for efficient height-based packing"""
        width, depth, height = item_dims
        
        # Find the space with the lowest maximum height that can fit the item
        best_space = None
        min_max_height = float('inf')
        
        for space in spaces:
            if space.can_fit(width, depth, height):
                max_height = space.z + height
                if max_height < min_max_height:
                    min_max_height = max_height
                    best_space = space
        
        if best_space:
            return (best_space, (best_space.x, best_space.y, best_space.z))
        return None
    
    def split_space_after_placement(self, original_space: Space3D, 
                                   item_pos: Tuple[float, float, float],
                                   item_dims: Tuple[float, float, float]) -> List[Space3D]:
        """
        Split remaining space after item placement using maximal rectangles algorithm
        """
        x, y, z = item_pos
        width, depth, height = item_dims
        
        new_spaces = []
        
        # Right space
        if x + width < original_space.x + original_space.width:
            right_space = Space3D(
                x + width, original_space.y, original_space.z,
                original_space.x + original_space.width - (x + width),
                original_space.depth,
                original_space.height
            )
            new_spaces.append(right_space)
        
        # Back space
        if y + depth < original_space.y + original_space.depth:
            back_space = Space3D(
                original_space.x, y + depth, original_space.z,
                original_space.width,
                original_space.y + original_space.depth - (y + depth),
                original_space.height
            )
            new_spaces.append(back_space)
        
        # Top space
        if z + height < original_space.z + original_space.height:
            top_space = Space3D(
                original_space.x, original_space.y, z + height,
                original_space.width,
                original_space.depth,
                original_space.z + original_space.height - (z + height)
            )
            new_spaces.append(top_space)
        
        return new_spaces
    
    def merge_adjacent_spaces(self, spaces: List[Space3D]) -> List[Space3D]:
        """Merge adjacent spaces to reduce fragmentation"""
        if len(spaces) <= 1:
            return spaces
        
        merged = []
        remaining = spaces.copy()
        
        while remaining:
            current = remaining.pop(0)
            merged_any = False
            
            # Try to merge with other spaces
            for i, other in enumerate(remaining):
                merged_space = self._try_merge_spaces(current, other)
                if merged_space:
                    remaining[i] = merged_space
                    merged_any = True
                    break
            
            if not merged_any:
                merged.append(current)
        
        return merged
    
    def _try_merge_spaces(self, space1: Space3D, space2: Space3D) -> Optional[Space3D]:
        """Try to merge two adjacent spaces"""
        # Check if spaces are adjacent and can be merged
        
        # Horizontal merge (along width axis)
        if (space1.y == space2.y and space1.z == space2.z and
            space1.depth == space2.depth and space1.height == space2.height):
            if space1.x + space1.width == space2.x:
                return Space3D(space1.x, space1.y, space1.z,
                             space1.width + space2.width,
                             space1.depth, space1.height)
            elif space2.x + space2.width == space1.x:
                return Space3D(space2.x, space1.y, space1.z,
                             space1.width + space2.width,
                             space1.depth, space1.height)
        
        # Depth merge (along depth axis)
        if (space1.x == space2.x and space1.z == space2.z and
            space1.width == space2.width and space1.height == space2.height):
            if space1.y + space1.depth == space2.y:
                return Space3D(space1.x, space1.y, space1.z,
                             space1.width,
                             space1.depth + space2.depth,
                             space1.height)
            elif space2.y + space2.depth == space1.y:
                return Space3D(space1.x, space2.y, space1.z,
                             space1.width,
                             space1.depth + space2.depth,
                             space1.height)
        
        # Height merge (along height axis)
        if (space1.x == space2.x and space1.y == space2.y and
            space1.width == space2.width and space1.depth == space2.depth):
            if space1.z + space1.height == space2.z:
                return Space3D(space1.x, space1.y, space1.z,
                             space1.width, space1.depth,
                             space1.height + space2.height)
            elif space2.z + space2.height == space1.z:
                return Space3D(space1.x, space1.y, space2.z,
                             space1.width, space1.depth,
                             space1.height + space2.height)
        
        return None
