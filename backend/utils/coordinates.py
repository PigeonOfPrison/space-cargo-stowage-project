from typing import Tuple, Dict, List
import math

class Coordinates3D:
    """Handles 3D coordinate system as specified in PDF"""
    
    def __init__(self, width: float, depth: float, height: float):
        self.width = width    # Horizontal along open face
        self.depth = depth    # Perpendicular to open face (into container)  
        self.height = height  # Vertical along open face
    
    def to_dict(self) -> Dict[str, float]:
        return {"width": self.width, "depth": self.depth, "height": self.height}
    
    @classmethod
    def from_dict(cls, coord_dict: Dict[str, float]) -> 'Coordinates3D':
        return cls(coord_dict["width"], coord_dict["depth"], coord_dict["height"])

class BoundingBox:
    """Represents 3D bounding box for items"""
    
    def __init__(self, start: Coordinates3D, end: Coordinates3D):
        self.start = start
        self.end = end
    
    def overlaps_with(self, other: 'BoundingBox', epsilon: float = 1e-5) -> bool:
        """Check if two bounding boxes overlap (collision detection)"""
        return not (
            self.end.width <= other.start.width + epsilon or
            self.start.width >= other.end.width - epsilon or
            self.end.depth <= other.start.depth + epsilon or
            self.start.depth >= other.end.depth - epsilon or
            self.end.height <= other.start.height + epsilon or
            self.start.height >= other.end.height - epsilon
        )
    
    def is_within_container(self, container_width: float, container_depth: float, 
                           container_height: float, epsilon: float = 1e-5) -> bool:
        """Check if bounding box fits within container bounds"""
        return (
            self.start.width >= -epsilon and self.end.width <= container_width + epsilon and
            self.start.depth >= -epsilon and self.end.depth <= container_depth + epsilon and
            self.start.height >= -epsilon and self.end.height <= container_height + epsilon
        )
    
    def get_volume(self) -> float:
        """Calculate bounding box volume"""
        return (
            (self.end.width - self.start.width) *
            (self.end.depth - self.start.depth) *
            (self.end.height - self.start.height)
        )
    
    def to_position_dict(self) -> Dict:
        """Convert to API response format"""
        return {
            "startCoordinates": self.start.to_dict(),
            "endCoordinates": self.end.to_dict()
        }

def calculate_distance_3d(point1: Coordinates3D, point2: Coordinates3D) -> float:
    """Calculate 3D Euclidean distance between two points"""
    return math.sqrt(
        (point2.width - point1.width) ** 2 +
        (point2.depth - point1.depth) ** 2 +
        (point2.height - point1.height) ** 2
    )

def generate_placement_positions(container_width: float, container_depth: float, 
                               container_height: float, item_w: float, item_d: float, 
                               item_h: float, occupied_boxes: List[BoundingBox]) -> List[BoundingBox]:
    """Generate potential placement positions for an item in a container - SIMPLIFIED FOR PERFORMANCE"""
    positions = []
    
    # Check if item fits at all
    if item_w > container_width or item_d > container_depth or item_h > container_height:
        return positions
    
    # SIMPLIFIED: Only try a few strategic positions instead of exhaustive search
    # This dramatically improves performance for large datasets
    
    candidate_positions = [
        # Try origin first (bottom-left-front corner)
        (0, 0, 0),
        # Try a few other positions if origin doesn't work
        (0, 0, container_height - item_h) if container_height > item_h else (0, 0, 0),
        (0, container_depth - item_d, 0) if container_depth > item_d else (0, 0, 0),
        (container_width - item_w, 0, 0) if container_width > item_w else (0, 0, 0),
    ]
    
    # Remove duplicates
    candidate_positions = list(set(candidate_positions))
    
    for start_w, start_d, start_h in candidate_positions:
        end_w = start_w + item_w
        end_d = start_d + item_d
        end_h = start_h + item_h
        
        # Check if position is within container bounds
        if (end_w <= container_width and 
            end_d <= container_depth and 
            end_h <= container_height):
            
            candidate_box = BoundingBox(
                Coordinates3D(start_w, start_d, start_h),
                Coordinates3D(end_w, end_d, end_h)
            )
            
            # Check for collisions with existing items
            collision = False
            for occupied_box in occupied_boxes:
                if candidate_box.overlaps_with(occupied_box):
                    collision = True
                    break
            
            if not collision:
                positions.append(candidate_box)
                # Return first valid position for performance
                break
    
    return positions
