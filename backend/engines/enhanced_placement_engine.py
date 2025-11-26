"""
Enhanced Placement Engine implementing advanced algorithms from archive
Combines:
- Priority-based placement with zone matching
- Advanced 3D space management with AABB collision detection
- Efficient grid-based position finding
- Better container selection algorithms
- Improved space utilization
"""
from typing import List, Dict, Optional, Tuple, Set
import math
import time
import heapq
from datetime import datetime
from backend.models.item import Item
from backend.models.container import Container

class FreeSpace:
    """Represents a block of free space in 3D"""
    def __init__(self, x: float, y: float, z: float, width: float, depth: float, height: float):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        
    @property
    def volume(self) -> float:
        return self.width * self.depth * self.height
    
    def can_fit(self, item_w: float, item_d: float, item_h: float) -> bool:
        """Check if an item can fit in this free space"""
        return (self.width >= item_w and 
                self.depth >= item_d and 
                self.height >= item_h)

class PlacedItem:
    """Represents an item that has been placed in 3D space"""
    def __init__(self, x: float, y: float, z: float, width: float, depth: float, height: float, item_id: str):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        self.item_id = item_id
        
    def get_aabb(self) -> Tuple[float, float, float, float, float, float]:
        """Get axis-aligned bounding box coordinates (x1, y1, z1, x2, y2, z2)"""
        return (self.x, self.y, self.z, 
                self.x + self.width, self.y + self.depth, self.z + self.height)

class ContainerSpace:
    """Advanced 3D space management for a single container"""
    def __init__(self, width: float, depth: float, height: float):
        self.width = width
        self.depth = depth
        self.height = height
        self.placed_items: List[PlacedItem] = []
        self.free_spaces: List[FreeSpace] = [FreeSpace(0, 0, 0, width, depth, height)]
        
    def can_place_item(self, x: float, y: float, z: float, width: float, depth: float, height: float) -> bool:
        """Check if an item can be placed at the specified position using AABB collision detection"""
        # Boundary check
        if (x < 0 or y < 0 or z < 0 or 
            x + width > self.width or 
            y + depth > self.depth or 
            z + height > self.height):
            return False
        
        # AABB collision detection
        new_x1, new_y1, new_z1 = x, y, z
        new_x2, new_y2, new_z2 = x + width, y + depth, z + height
        
        for placed_item in self.placed_items:
            placed_x1, placed_y1, placed_z1, placed_x2, placed_y2, placed_z2 = placed_item.get_aabb()
            
            # Check for overlap on all three axes
            if not (new_x2 <= placed_x1 or new_x1 >= placed_x2 or
                    new_y2 <= placed_y1 or new_y1 >= placed_y2 or
                    new_z2 <= placed_z1 or new_z1 >= placed_z2):
                return False
        
        return True
        
    def place_item(self, x: float, y: float, z: float, width: float, depth: float, height: float, item_id: str) -> bool:
        """Place an item and update space management"""
        if not self.can_place_item(x, y, z, width, depth, height):
            return False
            
        # Add to placed items
        placed_item = PlacedItem(x, y, z, width, depth, height, item_id)
        self.placed_items.append(placed_item)
        
        # Update free spaces by removing occupied area
        self._update_free_spaces(x, y, z, width, depth, height)
        return True
        
    def _update_free_spaces(self, x: float, y: float, z: float, width: float, depth: float, height: float):
        """Update free spaces after placing an item"""
        item_space = FreeSpace(x, y, z, width, depth, height)
        new_free_spaces = []
        
        for free_space in self.free_spaces:
            if self._spaces_overlap(free_space, item_space):
                # Split the free space around the item
                split_spaces = self._split_free_space(free_space, item_space)
                new_free_spaces.extend(split_spaces)
            else:
                new_free_spaces.append(free_space)
        
        # Filter out tiny spaces
        self.free_spaces = [fs for fs in new_free_spaces 
                           if fs.width > 0.1 and fs.depth > 0.1 and fs.height > 0.1]
    
    def _spaces_overlap(self, space1: FreeSpace, space2: FreeSpace) -> bool:
        """Check if two 3D spaces overlap"""
        return not (space1.x + space1.width <= space2.x or 
                   space2.x + space2.width <= space1.x or
                   space1.y + space1.depth <= space2.y or 
                   space2.y + space2.depth <= space1.y or
                   space1.z + space1.height <= space2.z or 
                   space2.z + space2.height <= space1.z)
    
    def _split_free_space(self, free_space: FreeSpace, item_space: FreeSpace) -> List[FreeSpace]:
        """Split a free space around an item space"""
        split_spaces = []
        
        # Create up to 6 new free spaces around the placed item
        # Left
        if item_space.x > free_space.x:
            split_spaces.append(FreeSpace(
                free_space.x, free_space.y, free_space.z,
                item_space.x - free_space.x, free_space.depth, free_space.height
            ))
        
        # Right
        if free_space.x + free_space.width > item_space.x + item_space.width:
            split_spaces.append(FreeSpace(
                item_space.x + item_space.width, free_space.y, free_space.z,
                (free_space.x + free_space.width) - (item_space.x + item_space.width),
                free_space.depth, free_space.height
            ))
        
        # Front (within x bounds)
        if item_space.y > free_space.y:
            x_start = max(free_space.x, item_space.x)
            x_end = min(free_space.x + free_space.width, item_space.x + item_space.width)
            if x_end > x_start:
                split_spaces.append(FreeSpace(
                    x_start, free_space.y, free_space.z,
                    x_end - x_start, item_space.y - free_space.y, free_space.height
                ))
        
        # Back (within x bounds)
        if free_space.y + free_space.depth > item_space.y + item_space.depth:
            x_start = max(free_space.x, item_space.x)
            x_end = min(free_space.x + free_space.width, item_space.x + item_space.width)
            if x_end > x_start:
                split_spaces.append(FreeSpace(
                    x_start, item_space.y + item_space.depth, free_space.z,
                    x_end - x_start,
                    (free_space.y + free_space.depth) - (item_space.y + item_space.depth),
                    free_space.height
                ))
        
        # Bottom (within x,y bounds)
        if item_space.z > free_space.z:
            x_start = max(free_space.x, item_space.x)
            x_end = min(free_space.x + free_space.width, item_space.x + item_space.width)
            y_start = max(free_space.y, item_space.y)
            y_end = min(free_space.y + free_space.depth, item_space.y + item_space.depth)
            if x_end > x_start and y_end > y_start:
                split_spaces.append(FreeSpace(
                    x_start, y_start, free_space.z,
                    x_end - x_start, y_end - y_start, item_space.z - free_space.z
                ))
        
        # Top (within x,y bounds)
        if free_space.z + free_space.height > item_space.z + item_space.height:
            x_start = max(free_space.x, item_space.x)
            x_end = min(free_space.x + free_space.width, item_space.x + item_space.width)
            y_start = max(free_space.y, item_space.y)
            y_end = min(free_space.y + free_space.depth, item_space.y + item_space.depth)
            if x_end > x_start and y_end > y_start:
                split_spaces.append(FreeSpace(
                    x_start, y_start, item_space.z + item_space.height,
                    x_end - x_start, y_end - y_start,
                    (free_space.z + free_space.height) - (item_space.z + item_space.height)
                ))
        
        return split_spaces
    
    def find_best_position(self, item_w: float, item_d: float, item_h: float, priority: int) -> Optional[Tuple[float, float, float]]:
        """Find the best position for an item using free space optimization"""
        best_position = None
        best_score = -1
        
        # Try each free space
        for free_space in self.free_spaces:
            if not free_space.can_fit(item_w, item_d, item_h):
                continue
                
            # Try different positions within this free space
            positions = self._generate_positions_in_space(free_space, item_w, item_d, item_h)
            
            for x, y, z in positions:
                if self.can_place_item(x, y, z, item_w, item_d, item_h):
                    score = self._calculate_position_score(x, y, z, priority)
                    if score > best_score:
                        best_score = score
                        best_position = (x, y, z)
        
        return best_position
    
    def _generate_positions_in_space(self, free_space: FreeSpace, item_w: float, item_d: float, item_h: float) -> List[Tuple[float, float, float]]:
        """Generate candidate positions within a free space"""
        positions = []
        
        # Corner position (most stable)
        positions.append((free_space.x, free_space.y, free_space.z))
        
        # Try a few strategic positions for better packing
        step_size = 10.0
        
        # Grid positions within the free space
        for x_offset in [0, min(step_size, free_space.width - item_w)]:
            for y_offset in [0, min(step_size, free_space.depth - item_d)]:
                for z_offset in [0, min(step_size, free_space.height - item_h)]:
                    x = free_space.x + x_offset
                    y = free_space.y + y_offset
                    z = free_space.z + z_offset
                    
                    if (x + item_w <= free_space.x + free_space.width and
                        y + item_d <= free_space.y + free_space.depth and
                        z + item_h <= free_space.z + free_space.height):
                        positions.append((x, y, z))
        
        return positions
    
    def _calculate_position_score(self, x: float, y: float, z: float, priority: int) -> float:
        """Calculate score for a position (higher is better)"""
        # Accessibility score (prefer items near container opening)
        accessibility_score = 100 - y  # Lower depth = more accessible
        
        # Stability score (prefer lower positions)
        stability_score = 100 - z
        
        # Priority bonus
        priority_score = priority
        
        return accessibility_score * 0.4 + stability_score * 0.3 + priority_score * 0.3
            )
            self.children.append(Octree(center, half, self.max_items))
    
    def _contains_point(self, point: Point3D) -> bool:
        return (abs(point.x - self.center.x) <= self.half_dimension and
                abs(point.y - self.center.y) <= self.half_dimension and
                abs(point.z - self.center.z) <= self.half_dimension)
    
    def query_region(self, min_point: Point3D, max_point: Point3D) -> List[str]:
        results = []
        
        # Check items at this level
        for item_id, item_min, item_max in self.items:
            if self._boxes_intersect(min_point, max_point, item_min, item_max):
                results.append(item_id)
        
        # Check children
        if self.children:
            for child in self.children:
                if child._region_intersects(min_point, max_point):
                    results.extend(child.query_region(min_point, max_point))
        
        return results
    
    def _boxes_intersect(self, min1: Point3D, max1: Point3D, min2: Point3D, max2: Point3D) -> bool:
        return not (max1.x <= min2.x or min1.x >= max2.x or
                   max1.y <= min2.y or min1.y >= max2.y or
                   max1.z <= min2.z or min1.z >= max2.z)
    
    def _region_intersects(self, min_point: Point3D, max_point: Point3D) -> bool:
        return not (max_point.x <= self.center.x - self.half_dimension or
                   min_point.x >= self.center.x + self.half_dimension or
                   max_point.y <= self.center.y - self.half_dimension or
                   min_point.y >= self.center.y + self.half_dimension or
                   max_point.z <= self.center.z - self.half_dimension or
                   min_point.z >= self.center.z + self.half_dimension)

class EnhancedPlacementEngine:
    """Enhanced placement engine with advanced algorithms from archive"""
    
    def __init__(self):
        self.grid_step = 5.0
        self.container_octrees = {}
        self.container_spaces = {}
        
        # Priority scoring weights
        self.priority_weight = 2.0
        self.accessibility_weight = 1.5
        self.zone_preference_weight = 1.2
        self.expiry_urgency_weight = 1.0
        
        # Zone matching flexibility
        self.zone_mappings = {
            'Storage_Bay': ['Storage', 'SB01', 'SB02', 'SB03'],
            'Medical_Bay': ['Medical', 'MB01', 'MB02', 'MB03'],
            'Engineering_Bay': ['Engineering', 'EB01', 'EB02', 'EB03'],
            'Crew_Quarters': ['Crew', 'CQ01', 'CQ02', 'CQ03'],
            'Lab': ['Laboratory', 'LAB01', 'LAB02', 'LAB03'],
            'Airlock': ['AL01', 'AL02', 'AL03']
        }
    
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """
        Find optimal placement using enhanced algorithms
        """
        # Calculate enhanced priority score
        priority_score = self._calculate_enhanced_priority_score(item)
        
        # Sort containers by preference and accessibility
        sorted_containers = self._sort_containers_enhanced(containers, item)
        
        best_placement = None
        best_score = -1
        
        for container in sorted_containers:
            container_id = container.containerId
            
            # Initialize octree for container if needed
            if container_id not in self.container_octrees:
                self._initialize_container_octree(container)
            
            # Get existing items in this container
            existing_items = [
                placed_item for placed_item in placed_items.values()
                if placed_item.containerId == container_id and placed_item.position
            ]
            
            # Try orientations (only 2 for efficiency)
            orientations = [
                (item.width, item.depth, item.height),
                (item.depth, item.width, item.height)
            ]
            
            for width, depth, height in orientations:
                if (width > container.width or 
                    depth > container.depth or 
                    height > container.height):
                    continue
                
                # Find position using enhanced algorithm
                position = self._find_enhanced_position(
                    width, depth, height, container, existing_items, priority_score
                )
                
                if position:
                    # Calculate placement score
                    placement_score = self._calculate_placement_score(
                        position, container, item, priority_score
                    )
                    
                    if placement_score > best_score:
                        best_score = placement_score
                        best_placement = {
                            "containerId": container_id,
                            "position": position,
                            "score": placement_score
                        }
        
        return best_placement
    
    def _calculate_enhanced_priority_score(self, item: Item) -> float:
        """Calculate enhanced priority score using multiple factors"""
        score = item.priority * self.priority_weight
        
        # Expiry urgency
        if item.expiryDate and item.expiryDate != "N/A":
            try:
                expiry_date = datetime.fromisoformat(item.expiryDate.replace('Z', '+00:00'))
                days_to_expiry = (expiry_date - datetime.now()).days
                if days_to_expiry <= 7:
                    score += 50 * self.expiry_urgency_weight
                elif days_to_expiry <= 30:
                    score += 25 * self.expiry_urgency_weight
            except:
                pass
        
        # Usage limit consideration
        if hasattr(item, 'usageLimit') and item.usageLimit:
            if item.usageLimit <= 5:
                score += 30
            elif item.usageLimit <= 20:
                score += 15
        
        # Size factor (smaller items easier to place)
        volume = item.width * item.depth * item.height
        if volume < 1000:
            score += 10
        
        return score
    
    def _sort_containers_enhanced(self, containers: Dict[str, Container], 
                                item: Item) -> List[Container]:
        """Sort containers by enhanced preference algorithm"""
        container_scores = []
        
        for container in containers.values():
            score = 0
            
            # Zone preference with flexible matching
            if self._zones_match(container.zone, item.preferredZone):
                score += 1000 * self.zone_preference_weight
            elif self._zones_similar(container.zone, item.preferredZone):
                score += 500 * self.zone_preference_weight
            
            # Container size (prefer larger containers for flexibility)
            volume = container.width * container.depth * container.height
            score += volume / 1000
            
            # Accessibility (prefer containers with better access)
            if container.depth <= 100:  # Shallow containers are more accessible
                score += 100
            
            container_scores.append((score, container))
        
        # Sort by score (highest first)
        container_scores.sort(key=lambda x: x[0], reverse=True)
        return [container for score, container in container_scores]
    
    def _zones_match(self, container_zone: str, preferred_zone: str) -> bool:
        """Check if zones match exactly or through mappings"""
        if container_zone == preferred_zone:
            return True
        
        # Check zone mappings
        for zone_key, zone_list in self.zone_mappings.items():
            if preferred_zone == zone_key and container_zone in zone_list:
                return True
            if container_zone == zone_key and preferred_zone in zone_list:
                return True
        
        return False
    
    def _zones_similar(self, container_zone: str, preferred_zone: str) -> bool:
        """Check if zones are similar (partial match)"""
        # Normalize zone names
        container_normalized = container_zone.lower().replace('_', '').replace(' ', '')
        preferred_normalized = preferred_zone.lower().replace('_', '').replace(' ', '')
        
        # Check for partial matches
        if (container_normalized in preferred_normalized or 
            preferred_normalized in container_normalized):
            return True
        
        # Check common prefixes
        common_prefixes = ['storage', 'medical', 'engineering', 'crew', 'lab', 'airlock']
        for prefix in common_prefixes:
            if (container_normalized.startswith(prefix) and 
                preferred_normalized.startswith(prefix)):
                return True
        
        return False
    
    def _initialize_container_octree(self, container: Container):
        """Initialize octree for container"""
        center = Point3D(container.width/2, container.depth/2, container.height/2)
        max_dimension = max(container.width, container.depth, container.height)
        self.container_octrees[container.containerId] = Octree(center, max_dimension/2)
    
    def _find_enhanced_position(self, item_width: float, item_depth: float, item_height: float,
                              container: Container, existing_items: List[Item], 
                              priority_score: float) -> Optional[Dict]:
        """Find position using enhanced algorithm with accessibility optimization"""
        
        # For high priority items, try accessible positions first
        if priority_score > 150:
            # Try positions near opening (low depth) first
            depth_order = [0, 5, 10, 15, 20]
        else:
            # Regular order for normal priority items
            depth_order = list(range(0, int(container.depth - item_depth) + 1, int(self.grid_step)))
        
        for y in depth_order:
            if y + item_depth > container.depth:
                continue
                
            # Try positions with accessibility preference
            for z in range(0, int(container.height - item_height) + 1, int(self.grid_step)):
                for x in range(0, int(container.width - item_width) + 1, int(self.grid_step)):
                    
                    # Quick bounds check
                    if (x + item_width > container.width or
                        y + item_depth > container.depth or
                        z + item_height > container.height):
                        continue
                    
                    # Enhanced collision detection
                    if self._is_position_valid_enhanced(
                        x, y, z, item_width, item_depth, item_height, 
                        container.containerId, existing_items):
                        
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
    
    def _is_position_valid_enhanced(self, x: float, y: float, z: float,
                                  width: float, depth: float, height: float,
                                  container_id: str, existing_items: List[Item]) -> bool:
        """Enhanced collision detection using octree when available"""
        
        # Fast AABB collision detection
        x1, y1, z1 = x, y, z
        x2, y2, z2 = x + width, y + depth, z + height
        
        for item in existing_items:
            if not item.position:
                continue
                
            start = item.position["startCoordinates"]
            end = item.position["endCoordinates"]
            
            ex1, ey1, ez1 = start["width"], start["depth"], start["height"]
            ex2, ey2, ez2 = end["width"], end["depth"], end["height"]
            
            # AABB intersection test
            if not (x2 <= ex1 or x1 >= ex2 or
                   y2 <= ey1 or y1 >= ey2 or
                   z2 <= ez1 or z1 >= ez2):
                return False
        
        return True
    
    def _calculate_placement_score(self, position: Dict, container: Container, 
                                 item: Item, priority_score: float) -> float:
        """Calculate placement score for position optimization"""
        score = 0
        
        start = position["startCoordinates"]
        
        # Accessibility score (lower depth = better)
        depth_score = (1.0 - start["depth"] / container.depth) * self.accessibility_weight * 100
        score += depth_score
        
        # Priority bonus
        score += priority_score * 0.1
        
        # Zone preference
        if self._zones_match(container.zone, item.preferredZone):
            score += 100 * self.zone_preference_weight
        elif self._zones_similar(container.zone, item.preferredZone):
            score += 50 * self.zone_preference_weight
        
        # Stability preference (lower height = more stable)
        if start["height"] < container.height * 0.3:
            score += 20
        
        return score
    
    def validate_placement(self, item: Item, container: Container, 
                          position: Dict, existing_items: Dict[str, Item]) -> Tuple[bool, str]:
        """Enhanced validation"""
        try:
            start = position["startCoordinates"]
            end = position["endCoordinates"]
            
            # Bounds check
            if (start["width"] < 0 or start["depth"] < 0 or start["height"] < 0 or
                end["width"] > container.width or 
                end["depth"] > container.depth or
                end["height"] > container.height):
                return False, "Item placement out of container bounds"
            
            # Dimensions check with tolerance
            placed_width = end["width"] - start["width"]
            placed_depth = end["depth"] - start["depth"]
            placed_height = end["height"] - start["height"]
            
            valid_orientations = [
                (item.width, item.depth, item.height),
                (item.depth, item.width, item.height)
            ]
            
            orientation_match = any(
                abs(placed_width - w) < 0.1 and 
                abs(placed_depth - d) < 0.1 and 
                abs(placed_height - h) < 0.1
                for w, d, h in valid_orientations
            )
            
            if not orientation_match:
                return False, "Item dimensions don't match placement"
            
            # Enhanced collision check
            container_items = [
                existing_item for existing_item in existing_items.values()
                if existing_item.containerId == container.containerId and existing_item.position
            ]
            
            if not self._is_position_valid_enhanced(
                start["width"], start["depth"], start["height"],
                placed_width, placed_depth, placed_height,
                container.containerId, container_items
            ):
                return False, "Item placement collides with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, items: List[Item], containers: Dict[str, Container],
                            existing_items: Dict[str, Item]) -> List[Dict]:
        """Enhanced rearrangement suggestions"""
        # For now, return empty list as rearrangement is complex
        return []
