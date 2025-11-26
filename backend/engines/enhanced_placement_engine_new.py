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
        """Place an item and update space management - simplified version"""
        if not self.can_place_item(x, y, z, width, depth, height):
            return False
            
        # Add to placed items
        placed_item = PlacedItem(x, y, z, width, depth, height, item_id)
        self.placed_items.append(placed_item)
        
        # Simplified free space update - just remove the largest overlapping free space
        new_free_spaces = []
        for free_space in self.free_spaces:
            if not self._spaces_overlap(free_space, FreeSpace(x, y, z, width, depth, height)):
                new_free_spaces.append(free_space)
        
        self.free_spaces = new_free_spaces
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
        """Find the best position for an item using simplified logic initially"""
        # First check if item fits at origin
        if self.can_place_item(0, 0, 0, item_w, item_d, item_h):
            return (0.0, 0.0, 0.0)
        
        # Try grid positions
        step_size = 10.0
        max_x = max(0, self.width - item_w)
        max_y = max(0, self.depth - item_d)
        max_z = max(0, self.height - item_h)
        
        best_position = None
        best_score = -1
        
        # Try positions in a grid
        for z in [0, min(step_size, max_z)]:
            for y in [0, min(step_size, max_y), min(step_size * 2, max_y)]:
                for x in [0, min(step_size, max_x), min(step_size * 2, max_x)]:
                    if (x <= max_x and y <= max_y and z <= max_z and
                        self.can_place_item(x, y, z, item_w, item_d, item_h)):
                        
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

class EnhancedPlacementEngine:
    """Enhanced placement engine with advanced algorithms from archive"""
    
    def __init__(self):
        self.container_spaces: Dict[str, ContainerSpace] = {}
        self.containers_data: Dict[str, Container] = {}
        
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """Find optimal placement using enhanced algorithms"""
        
        # Initialize container spaces if needed
        self._initialize_container_spaces(containers)
        
        # Get valid orientations
        orientations = [
            (item.width, item.depth, item.height),  # Original
            (item.depth, item.width, item.height)   # 90° rotation
        ]
        
        # Sort containers by suitability
        sorted_containers = self._sort_containers_by_suitability(containers, item)
        
        best_placement = None
        best_score = -1
        
        for container in sorted_containers:
            container_id = container.containerId
            container_space = self.container_spaces.get(container_id)
            
            if not container_space:
                continue
            
            # Try each orientation
            for width, depth, height in orientations:
                if not self._fits_in_container(width, depth, height, container):
                    continue
                
                # Find best position in this container
                position = container_space.find_best_position(width, depth, height, item.priority)
                
                if position:
                    x, y, z = position
                    # Calculate overall placement score
                    placement_score = self._calculate_placement_score(
                        item, container, x, y, z
                    )
                    
                    if placement_score > best_score:
                        best_score = placement_score
                        best_placement = {
                            "containerId": container_id,
                            "position": {
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
                        }
        
        # If placement found, update container space
        if best_placement:
            container_id = best_placement["containerId"]
            pos = best_placement["position"]
            start = pos["startCoordinates"]
            end = pos["endCoordinates"]
            
            width = end["width"] - start["width"]
            depth = end["depth"] - start["depth"]
            height = end["height"] - start["height"]
            
            self.container_spaces[container_id].place_item(
                start["width"], start["depth"], start["height"],
                width, depth, height, item.itemId
            )
        
        return best_placement
    
    def find_optimal_placement_debug(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """Debug version of find_optimal_placement"""
        print(f"DEBUG: Placing item {item.itemId} with dimensions {item.width}x{item.depth}x{item.height}")
        
        # Initialize container spaces if needed
        self._initialize_container_spaces(containers)
        print(f"DEBUG: Initialized {len(self.container_spaces)} container spaces")
        
        # Get valid orientations
        orientations = [
            (item.width, item.depth, item.height),  # Original
            (item.depth, item.width, item.height)   # 90° rotation
        ]
        print(f"DEBUG: Trying {len(orientations)} orientations: {orientations}")
        
        # Sort containers by suitability
        sorted_containers = self._sort_containers_by_suitability(containers, item)
        print(f"DEBUG: Sorted {len(sorted_containers)} containers by suitability")
        
        best_placement = None
        best_score = -1
        
        for i, container in enumerate(sorted_containers):
            container_id = container.containerId
            container_space = self.container_spaces.get(container_id)
            print(f"DEBUG: Trying container {i+1}/{len(sorted_containers)}: {container_id}")
            
            if not container_space:
                print(f"DEBUG: No container space for {container_id}")
                continue
            
            suitability_score = self._calculate_container_suitability(container, item)
            print(f"DEBUG: Container {container_id} suitability score: {suitability_score}")
            
            # Try each orientation
            for j, (width, depth, height) in enumerate(orientations):
                print(f"DEBUG: Trying orientation {j+1}: {width}x{depth}x{height}")
                
                if not self._fits_in_container(width, depth, height, container):
                    print(f"DEBUG: Orientation {j+1} doesn't fit in container {container_id}")
                    continue
                
                print(f"DEBUG: Orientation {j+1} fits, looking for position...")
                
                # Find best position in this container
                position = container_space.find_best_position(width, depth, height, item.priority)
                
                if position:
                    x, y, z = position
                    print(f"DEBUG: Found position: ({x}, {y}, {z})")
                    
                    # Calculate overall placement score
                    placement_score = self._calculate_placement_score(
                        item, container, x, y, z
                    )
                    print(f"DEBUG: Placement score: {placement_score}")
                    
                    if placement_score > best_score:
                        best_score = placement_score
                        best_placement = {
                            "containerId": container_id,
                            "position": {
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
                        }
                        print(f"DEBUG: New best placement found with score {best_score}")
                else:
                    print(f"DEBUG: No position found for orientation {j+1}")
        
        if best_placement:
            print(f"DEBUG: Final best placement: {best_placement}")
        else:
            print(f"DEBUG: No placement found for item {item.itemId}")
            
        return best_placement
    
    def _initialize_container_spaces(self, containers: Dict[str, Container]):
        """Initialize container spaces for advanced space management"""
        for container_id, container in containers.items():
            if container_id not in self.container_spaces:
                self.container_spaces[container_id] = ContainerSpace(
                    container.width, container.depth, container.height
                )
                self.containers_data[container_id] = container
    
    def _sort_containers_by_suitability(self, containers: Dict[str, Container], item: Item) -> List[Container]:
        """Sort containers by suitability for the item"""
        container_scores = []
        
        for container in containers.values():
            score = self._calculate_container_suitability(container, item)
            container_scores.append((score, container))
        
        container_scores.sort(key=lambda x: x[0], reverse=True)
        return [container for score, container in container_scores]
    
    def _calculate_container_suitability(self, container: Container, item: Item) -> float:
        """Calculate how suitable a container is for an item"""
        score = 0.0
        
        # Zone matching (highest priority)
        if self._is_zone_match(item.preferredZone, container.zone):
            score += 1000
        else:
            score += 500  # Increased base score for any container when no zone match
        
        # Space efficiency (prefer containers that aren't too large)
        container_volume = container.width * container.depth * container.height
        item_volume = item.width * item.depth * item.height
        if container_volume > 0:
            efficiency = item_volume / container_volume
            score += efficiency * 100
        
        # Available free space
        container_space = self.container_spaces.get(container.containerId)
        if container_space:
            free_volume = sum(fs.volume for fs in container_space.free_spaces)
            if free_volume >= item_volume:
                score += min(free_volume / item_volume, 10) * 50
        
        return score
    
    def _is_zone_match(self, preferred: str, container_zone: str) -> bool:
        """Check if item's preferred zone matches container zone"""
        if not preferred or not container_zone:
            return False
            
        pref_clean = preferred.lower().replace('_', '').replace(' ', '').replace('-', '')
        cont_clean = container_zone.lower().replace('_', '').replace(' ', '').replace('-', '')
        
        # Exact match
        if pref_clean == cont_clean:
            return True
            
        # Partial matches
        if pref_clean in cont_clean or cont_clean in pref_clean:
            return True
            
        # Keyword-based matching for common zone types
        zone_keywords = {
            'lab': ['lab', 'research', 'science', 'experiment'],
            'storage': ['storage', 'bay', 'cargo', 'warehouse'],
            'maintenance': ['maintenance', 'engineering', 'repair', 'workshop'],
            'crew': ['crew', 'quarters', 'living', 'personal'],
            'medical': ['medical', 'health', 'hospital', 'clinic'],
            'airlock': ['airlock', 'entry', 'exit', 'docking'],
            'cockpit': ['cockpit', 'bridge', 'control', 'command']
        }
        
        for zone_type, keywords in zone_keywords.items():
            pref_match = any(keyword in pref_clean for keyword in keywords)
            cont_match = any(keyword in cont_clean for keyword in keywords)
            if pref_match and cont_match:
                return True
        
        return False
    
    def _fits_in_container(self, width: float, depth: float, height: float, container: Container) -> bool:
        """Check if item dimensions fit in container"""
        return (width <= container.width and 
                depth <= container.depth and 
                height <= container.height)
    
    def _calculate_placement_score(self, item: Item, container: Container, x: float, y: float, z: float) -> float:
        """Calculate overall placement score"""
        score = 0.0
        
        # Zone preference (important but not blocking)
        if self._is_zone_match(item.preferredZone, container.zone):
            score += 1000
        else:
            score += 200  # Still give a reasonable score for non-matching zones
        
        # Priority weighting
        score += item.priority * 10
        
        # Accessibility (prefer positions near opening)
        accessibility = max(0, 100 - y)
        score += accessibility * 2
        
        # Stability (prefer lower positions)
        stability = max(0, 100 - z)
        score += stability
        
        return score
    
    def place_items(self, items: List[Item], containers: Dict[str, Container]) -> List[Dict]:
        """Place multiple items with enhanced algorithms"""
        # Sort items by enhanced priority
        sorted_items = self._sort_items_by_priority(items)
        
        placements = []
        placed_items = {}
        
        for item in sorted_items:
            placement = self.find_optimal_placement(item, containers, placed_items)
            if placement:
                placements.append({
                    "itemId": item.itemId,
                    "containerId": placement["containerId"],
                    "position": placement["position"]
                })
                placed_items[item.itemId] = item
        
        return placements
    
    def _sort_items_by_priority(self, items: List[Item]) -> List[Item]:
        """Sort items by enhanced priority considering multiple factors"""
        def calculate_priority_score(item: Item) -> float:
            score = item.priority * 100  # Base priority
            
            # Size factor (smaller items first for better packing)
            volume = item.width * item.depth * item.height
            if volume < 1000:  # Small items
                score += 50
            elif volume > 10000:  # Large items (place early)
                score += 25
            
            return score
        
        return sorted(items, key=calculate_priority_score, reverse=True)
    
    def validate_placement(self, item: Item, container: Container, 
                          position: Dict, existing_items: Dict[str, Item]) -> Tuple[bool, str]:
        """Validate placement with improved checks"""
        try:
            start = position["startCoordinates"]
            end = position["endCoordinates"]
            
            # Bounds check
            if (start["width"] < 0 or start["depth"] < 0 or start["height"] < 0 or
                end["width"] > container.width or 
                end["depth"] > container.depth or
                end["height"] > container.height):
                return False, "Item placement out of container bounds"
            
            # Dimension check
            placed_width = end["width"] - start["width"]
            placed_depth = end["depth"] - start["depth"]
            placed_height = end["height"] - start["height"]
            
            # Check valid orientations
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
                return False, f"Invalid dimensions: {placed_width}x{placed_depth}x{placed_height}"
            
            # Check if placement is possible using our advanced collision detection
            container_space = self.container_spaces.get(container.containerId)
            if container_space:
                can_place = container_space.can_place_item(
                    start["width"], start["depth"], start["height"],
                    placed_width, placed_depth, placed_height
                )
                if not can_place:
                    return False, "Collision with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, items: List[Item], containers: Dict[str, Container],
                            existing_items: Dict[str, Item]) -> List[Dict]:
        """Suggest rearrangement operations"""
        return []  # Simplified for now

    def _get_container_items(self, container_id: str, placed_items: Dict[str, Item]) -> List[Dict]:
        """Get items that have been placed in a specific container - compatibility method"""
        container_space = self.container_spaces.get(container_id)
        if not container_space:
            return []
        
        # Convert internal format to expected format
        items = []
        for placed_item in container_space.placed_items:
            items.append({
                'itemId': placed_item.item_id,
                'bounds': {
                    'startCoordinates': {
                        'width': placed_item.x,
                        'depth': placed_item.y,
                        'height': placed_item.z
                    },
                    'endCoordinates': {
                        'width': placed_item.x + placed_item.width,
                        'depth': placed_item.y + placed_item.depth,
                        'height': placed_item.z + placed_item.height
                    }
                }
            })
        return items
