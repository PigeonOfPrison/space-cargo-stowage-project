"""
Core placement algorithm utilities
Focused on efficiency and PDF compliance
"""
from typing import List, Tuple, Dict, Optional
from backend.models.item import Item
from backend.models.container import Container

class PlacementUtils:
    """Utility functions for placement calculations"""
    
    @staticmethod
    def get_item_orientations(item: Item) -> List[Tuple[float, float, float]]:
        """
        Get valid orientations for an item
        Per PDF: items can be rotated (width/depth swap)
        """
        return [
            (item.width, item.depth, item.height),  # Original
            (item.depth, item.width, item.height)   # 90° rotation
        ]
    
    @staticmethod
    def fits_in_container(width: float, depth: float, height: float, 
                         container: Container) -> bool:
        """Check if item dimensions fit in container"""
        return (width <= container.width and 
                depth <= container.depth and 
                height <= container.height)
    
    @staticmethod
    def calculate_priority_score(item: Item) -> float:
        """
        Calculate priority score for sorting
        Higher score = higher priority
        """
        base_score = item.priority
        
        # Bonus for high priority items
        if item.priority >= 90:
            base_score += 10
        elif item.priority >= 80:
            base_score += 5
            
        return base_score
    
    @staticmethod
    def normalize_zone_name(zone: str) -> str:
        """Normalize zone names for flexible matching"""
        return zone.lower().replace('_', '').replace(' ', '').replace('-', '')
    
    @staticmethod
    def zones_match(preferred_zone: str, container_zone: str) -> int:
        """
        Calculate zone match score
        0 = no match, 1 = partial match, 2 = exact match
        """
        pref_norm = PlacementUtils.normalize_zone_name(preferred_zone)
        cont_norm = PlacementUtils.normalize_zone_name(container_zone)
        
        if pref_norm == cont_norm:
            return 2  # Exact match
        elif (pref_norm in cont_norm or cont_norm in pref_norm or
              any(word in cont_norm for word in pref_norm.split()) or
              any(word in pref_norm for word in cont_norm.split())):
            return 1  # Partial match
        else:
            return 0  # No match

    @staticmethod
    def find_best_positions(container: Container, width: float, depth: float, height: float,
                           max_positions: int = 10, grid_step: float = 10.0) -> List[Tuple[float, float, float]]:
        """
        Generate candidate positions for placement
        Prioritizes accessible positions (near opening)
        """
        positions = []
        
        # Always try the most accessible position first
        if (width <= container.width and depth <= container.depth and height <= container.height):
            positions.append((0.0, 0.0, 0.0))
        
        # Generate grid positions with accessibility priority
        step_w = min(grid_step, container.width / 5)
        step_d = min(grid_step, container.depth / 5)
        step_h = min(grid_step, container.height / 5)
        
        w_steps = min(int((container.width - width) / step_w) + 1, 5)
        d_steps = min(int((container.depth - depth) / step_d) + 1, 5)
        h_steps = min(int((container.height - height) / step_h) + 1, 5)
        
        # Generate positions, prioritizing low depth (accessible)
        for d_idx in range(d_steps):
            for h_idx in range(h_steps):
                for w_idx in range(w_steps):
                    if len(positions) >= max_positions:
                        break
                    
                    x = w_idx * step_w
                    y = d_idx * step_d
                    z = h_idx * step_h
                    
                    # Ensure within bounds
                    if (x + width <= container.width and
                        y + depth <= container.depth and
                        z + height <= container.height):
                        
                        pos = (float(x), float(y), float(z))
                        if pos not in positions:
                            positions.append(pos)
        
        return positions
    
    @staticmethod
    def create_position_dict(x: float, y: float, z: float,
                           width: float, depth: float, height: float) -> Dict:
        """
        Create position dictionary in PDF-compliant format
        """
        return {
            "startCoordinates": {
                "width": float(x),
                "depth": float(y),
                "height": float(z)
            },
            "endCoordinates": {
                "width": float(x + width),
                "depth": float(y + depth),
                "height": float(z + height)
            }
        }
