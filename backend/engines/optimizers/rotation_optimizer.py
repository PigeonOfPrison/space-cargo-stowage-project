"""
Rotation Optimizer - Advanced rotation and orientation handling
"""
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RotationOptimizer:
    """Advanced rotation optimizer with stability and space efficiency focus"""
    
    def __init__(self):
        self.rotation_cache = {}
        
    def get_all_orientations(self, width: float, depth: float, height: float) -> List[Tuple[float, float, float]]:
        """
        Generate all 6 possible orientations for an item with stability scoring
        Returns list of (w, d, h) tuples sorted by preference
        """
        base_dims = (width, depth, height)
        cache_key = base_dims
        
        if cache_key in self.rotation_cache:
            return self.rotation_cache[cache_key]
        
        # All 6 orientations
        orientations = [
            (width, depth, height),  # Original
            (width, height, depth),  # Rotate around width axis
            (depth, width, height),  # Rotate around height axis
            (depth, height, width),  # Rotate around width then height
            (height, width, depth),  # Rotate around depth axis
            (height, depth, width),  # Rotate around depth then width
        ]
        
        # Remove duplicates while preserving order
        unique_orientations = []
        seen = set()
        for orient in orientations:
            if orient not in seen:
                unique_orientations.append(orient)
                seen.add(orient)
        
        # Score and sort orientations by stability and space efficiency
        scored_orientations = []
        for w, d, h in unique_orientations:
            stability_score = self._calculate_stability_score(w, d, h)
            space_efficiency = self._calculate_space_efficiency(w, d, h)
            total_score = stability_score + space_efficiency
            scored_orientations.append((total_score, (w, d, h)))
        
        # Sort by score (higher is better)
        scored_orientations.sort(reverse=True)
        result = [orient for score, orient in scored_orientations]
        
        self.rotation_cache[cache_key] = result
        return result
    
    def _calculate_stability_score(self, width: float, depth: float, height: float) -> float:
        """Calculate stability score - lower center of gravity is better"""
        base_area = width * depth
        if height == 0:
            return 1000  # Flat items are very stable
        
        # Lower height relative to base area is more stable
        stability = base_area / (height + 1)
        
        # Bonus for square-ish base (more stable)
        aspect_ratio = max(width, depth) / min(width, depth) if min(width, depth) > 0 else 1
        square_bonus = 1 / aspect_ratio
        
        return stability * (1 + square_bonus)
    
    def _calculate_space_efficiency(self, width: float, depth: float, height: float) -> float:
        """Calculate how space-efficient this orientation is for packing"""
        # Prefer orientations that minimize unused space
        volume = width * depth * height
        if volume == 0:
            return 0
        
        # Prefer orientations with dimensions that are easier to pack around
        # Avoid very thin dimensions that create hard-to-use spaces
        dimension_balance = min(width, depth, height) / max(width, depth, height)
        
        return dimension_balance * 100
    
    def find_best_orientation(self, item_dims: Tuple[float, float, float], 
                            available_space: Tuple[float, float, float],
                            container_dims: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Find the best orientation for an item given available space and container constraints
        """
        width, depth, height = item_dims
        space_w, space_d, space_h = available_space
        container_w, container_d, container_h = container_dims
        
        orientations = self.get_all_orientations(width, depth, height)
        
        for w, d, h in orientations:
            # Check if orientation fits in available space
            if w <= space_w and d <= space_d and h <= space_h:
                # Additional check: ensure it fits in container overall
                if w <= container_w and d <= container_d and h <= container_h:
                    return (w, d, h)
        
        # Return original if no orientation fits
        return (width, depth, height)
    
    def validate_rotation(self, original_dims: Tuple[float, float, float], 
                         placed_dims: Tuple[float, float, float]) -> bool:
        """Validate that placed dimensions are a valid rotation of original"""
        orig_sorted = tuple(sorted(original_dims))
        placed_sorted = tuple(sorted(placed_dims))
        return orig_sorted == placed_sorted
