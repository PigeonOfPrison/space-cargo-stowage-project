from typing import List, Optional, Tuple, Dict
from backend.models.item import Item
from backend.models.container import Container
from backend.utils.coordinates import Coordinates3D, BoundingBox
import heapq

class SpatialEngine:
    """Fast 3D bin packing with grid-based placement"""
    
    def __init__(self):
        self.epsilon = 1e-5  # Floating point tolerance
        self.grid_size = 5.0  # 5cm grid for placement positions
    
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """
        Fast placement algorithm using grid-based approach
        Returns: {containerId: str, position: dict, rotation_used: tuple}
        """
        # Prepare container spaces for fast lookup
        container_spaces = self._prepare_container_spaces(containers, placed_items)
        
        # Try to place item using fast algorithm
        placement = self._place_item_fast(item, container_spaces)
        
        if placement:
            return {
                "containerId": placement["containerId"],
                "position": placement["position"],
                "rotation_used": placement.get("rotation_used", (item.width, item.depth, item.height))
            }
        
        return None
    
    def _prepare_container_spaces(self, containers: Dict[str, Container], 
                                placed_items: Dict[str, Item]) -> Dict:
        """Prepare container space information for fast placement"""
        container_spaces = {}
        
        for container_id, container in containers.items():
            # Calculate occupied volume
            occupied_volume = 0
            occupied_positions = []
            
            for item in placed_items.values():
                if item.containerId == container_id and item.position:
                    # Add occupied position
                    start = item.position["startCoordinates"]
                    end = item.position["endCoordinates"]
                    occupied_positions.append({
                        "start": start,
                        "end": end
                    })
                    
                    # Calculate volume
                    volume = ((end["width"] - start["width"]) * 
                             (end["depth"] - start["depth"]) * 
                             (end["height"] - start["height"]))
                    occupied_volume += volume
            
            container_volume = container.width * container.depth * container.height
            available_space = container_volume - occupied_volume
            
            container_spaces[container_id] = {
                "container": container,
                "width": container.width,
                "depth": container.depth, 
                "height": container.height,
                "available_space": available_space,
                "occupied_positions": occupied_positions,
                "zone": container.zone
            }
        
        return container_spaces
    
    def _place_item_fast(self, item: Item, container_spaces: Dict) -> Optional[Dict]:
        """Ultra-fast placement algorithm using grid-based approach"""
        # Try item orientations (only 2 main rotations to keep it simple)
        orientations = [
            (item.width, item.depth, item.height),
            (item.depth, item.width, item.height)
        ]
        
        # Sort containers by preference (preferred zone first, then by available space)
        container_priority = []
        for container_id, space_info in container_spaces.items():
            priority = 0
            if space_info["zone"] == item.preferredZone:
                priority += 1000  # High priority for preferred zone
            priority += space_info["available_space"]  # More space = higher priority
            container_priority.append((priority, container_id, space_info))
        
        container_priority.sort(reverse=True)  # Highest priority first
        
        # Try containers in priority order
        for _, container_id, space_info in container_priority:
            # Skip if container doesn't have enough volume
            item_volume = item.width * item.depth * item.height
            if item_volume > space_info['available_space']:
                continue
                
            # Try each orientation
            for width, depth, height in orientations:
                # Quick bounds check
                if (width > space_info['width'] or 
                    depth > space_info['depth'] or 
                    height > space_info['height']):
                    continue
                
                # Find position using grid-based algorithm
                position = self._find_grid_position(width, depth, height, space_info)
                
                if position:
                    # Create placement record
                    x, y, z = position
                    return {
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
                        },
                        "rotation_used": (width, depth, height)
                    }
        return None
    
    def _find_grid_position(self, item_width: float, item_depth: float, 
                           item_height: float, space_info: Dict) -> Optional[Tuple[float, float, float]]:
        """Find valid position using grid-based search"""
        container_width = space_info["width"]
        container_depth = space_info["depth"]
        container_height = space_info["height"]
        occupied_positions = space_info["occupied_positions"]
        
        # Calculate grid steps (limit to reasonable number for performance)
        max_steps = 20  # Maximum 20 steps per dimension
        
        width_step = max(self.grid_size, (container_width - item_width) / max_steps) if container_width > item_width else container_width
        depth_step = max(self.grid_size, (container_depth - item_depth) / max_steps) if container_depth > item_depth else container_depth
        height_step = max(self.grid_size, (container_height - item_height) / max_steps) if container_height > item_height else container_height
        
        # Try positions on grid
        z = 0  # Start from bottom (height = 0)
        while z + item_height <= container_height:
            y = 0  # Start from front (depth = 0, closest to opening)
            while y + item_depth <= container_depth:
                x = 0  # Start from left (width = 0)
                while x + item_width <= container_width:
                    
                    # Check if this position collides with any occupied positions
                    if not self._position_collides(x, y, z, item_width, item_depth, 
                                                 item_height, occupied_positions):
                        return (x, y, z)
                    
                    x += width_step
                    if x + item_width > container_width:
                        break
                
                y += depth_step
                if y + item_depth > container_depth:
                    break
            
            z += height_step
            if z + item_height > container_height:
                break
        
        return None
    
    def _position_collides(self, x: float, y: float, z: float, 
                          width: float, depth: float, height: float,
                          occupied_positions: List[Dict]) -> bool:
        """Check if position collides with any occupied positions"""
        item_end_x = x + width
        item_end_y = y + depth
        item_end_z = z + height
        
        for occupied in occupied_positions:
            occ_start = occupied["start"]
            occ_end = occupied["end"]
            
            # Check for overlap using separation test
            if not (item_end_x <= occ_start["width"] + self.epsilon or
                    x >= occ_end["width"] - self.epsilon or
                    item_end_y <= occ_start["depth"] + self.epsilon or
                    y >= occ_end["depth"] - self.epsilon or
                    item_end_z <= occ_start["height"] + self.epsilon or
                    z >= occ_end["height"] - self.epsilon):
                return True  # Collision detected
        
        return False  # No collision
            
            # Skip if container is in wrong zone and no space pressure
            zone_penalty = 0
            if container.zone != item.preferredZone:
                zone_penalty = 30  # Penalty for wrong zone
            
            for rotation in rotations:
                item_w, item_d, item_h = rotation
                print(f"DEBUG: Trying rotation {rotation}")
                
                # Quick volume check
                item_volume = item_w * item_d * item_h
                can_fit = container.can_fit_item(item_volume, placed_items)
                print(f"DEBUG: Item volume: {item_volume}, can fit: {can_fit}")
                
                if not can_fit:
                    continue
                
                # Get occupied positions in this container
                occupied_boxes = self._get_occupied_boxes(container_id, placed_items)
                print(f"DEBUG: Occupied boxes: {len(occupied_boxes)}")
                
                # Generate potential positions
                potential_positions = generate_placement_positions(
                    container.width, container.depth, container.height,
                    item_w, item_d, item_h, occupied_boxes
                )
                print(f"DEBUG: Generated {len(potential_positions)} potential positions")
                
                for position_box in potential_positions:
                    # Calculate placement score
                    score = self._calculate_placement_score(
                        item, container, position_box, placed_items, zone_penalty
                    )
                    print(f"DEBUG: Position score: {score}")
                    
                    if score > best_score:
                        best_score = score
                        best_placement = {
                            "containerId": container_id,
                            "position": position_box.to_position_dict(),
                            "rotation_used": rotation
                        }
        
        print(f"DEBUG: Best placement: {best_placement}")
        return best_placement
    
    def _get_occupied_boxes(self, container_id: str, placed_items: Dict[str, Item]) -> List[BoundingBox]:
        """Get bounding boxes of all items in a container"""
        boxes = []
        
        for item in placed_items.values():
            if item.containerId == container_id and item.position:
                start_coords = Coordinates3D.from_dict(item.position["startCoordinates"])
                end_coords = Coordinates3D.from_dict(item.position["endCoordinates"])
                boxes.append(BoundingBox(start_coords, end_coords))
        
        return boxes
    
    def _calculate_placement_score(self, item: Item, container: Container, 
                                 position_box: BoundingBox, placed_items: Dict[str, Item],
                                 zone_penalty: float) -> float:
        """Calculate placement score based on multiple factors"""
        score = 0.0
        
        # Priority factor (higher priority = higher score)
        score += item.get_priority_score() * 2
        
        # Zone preference (preferred zone gets bonus)
        if container.zone == item.preferredZone:
            score += 50
        else:
            score -= zone_penalty
        
        # Accessibility factor (closer to opening = higher score)
        # Items closer to depth=0 (opening) are more accessible
        depth_accessibility = container.depth - position_box.start.depth
        score += (depth_accessibility / container.depth) * 30
        
        # Height accessibility (lower items are easier to reach)
        height_accessibility = container.height - position_box.start.height
        score += (height_accessibility / container.height) * 20
        
        # Utilization factor (prefer placements that utilize space efficiently)
        container_volume = container.get_volume()
        used_volume = container.get_used_volume(placed_items)
        utilization_after = (used_volume + position_box.get_volume()) / container_volume
        
        # Prefer moderate utilization (not too cramped, not too sparse)
        optimal_utilization = 0.75
        utilization_score = 100 - abs(utilization_after - optimal_utilization) * 100
        score += utilization_score * 0.3
        
        # Stacking efficiency (prefer bottom-up placement)
        if position_box.start.height == 0:  # Ground level
            score += 15
        
        return score
    
    def check_collision(self, new_position: Dict, container_id: str, 
                       placed_items: Dict[str, Item], ignore_item_id: str = None) -> bool:
        """Check if a new position collides with existing items"""
        new_start = Coordinates3D.from_dict(new_position["startCoordinates"])
        new_end = Coordinates3D.from_dict(new_position["endCoordinates"])
        new_box = BoundingBox(new_start, new_end)
        
        for item in placed_items.values():
            if (item.containerId == container_id and 
                item.position and 
                item.itemId != ignore_item_id):
                
                existing_start = Coordinates3D.from_dict(item.position["startCoordinates"])
                existing_end = Coordinates3D.from_dict(item.position["endCoordinates"])
                existing_box = BoundingBox(existing_start, existing_end)
                
                if new_box.overlaps_with(existing_box):
                    return True
        
        return False
    
    def validate_placement(self, item: Item, container: Container, 
                          position: Dict, placed_items: Dict[str, Item]) -> Tuple[bool, str]:
        """Validate if a placement is valid"""
        try:
            # Check coordinate structure
            start = Coordinates3D.from_dict(position["startCoordinates"])
            end = Coordinates3D.from_dict(position["endCoordinates"])
            box = BoundingBox(start, end)
            
            # Check container bounds
            if not box.is_within_container(container.width, container.depth, container.height):
                return False, "Item exceeds container bounds"
            
            # Check dimensions match item (considering rotations)
            placed_w = end.width - start.width
            placed_d = end.depth - start.depth
            placed_h = end.height - start.height
            
            valid_rotations = item.get_rotations()
            dimension_match = False
            
            for rotation in valid_rotations:
                if (abs(placed_w - rotation[0]) < self.epsilon and
                    abs(placed_d - rotation[1]) < self.epsilon and
                    abs(placed_h - rotation[2]) < self.epsilon):
                    dimension_match = True
                    break
            
            if not dimension_match:
                return False, f"Dimensions don't match any valid rotation. Placed: ({placed_w}, {placed_d}, {placed_h}), Valid: {valid_rotations}"
            
            # Check collisions
            if self.check_collision(position, container.containerId, placed_items, item.itemId):
                return False, "Collision with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, new_items: List[Item], containers: Dict[str, Container],
                            placed_items: Dict[str, Item]) -> List[Dict]:
        """Suggest rearrangement steps to accommodate new items"""
        rearrangement_steps = []
        step_counter = 1
        
        # Sort new items by priority (high priority first)
        new_items_sorted = sorted(new_items, key=lambda x: x.get_priority_score(), reverse=True)
        
        for new_item in new_items_sorted:
            # Try to find placement without rearrangement first
            placement = self.find_optimal_placement(new_item, containers, placed_items)
            
            if placement:
                continue  # Can place without rearrangement
            
            # Need rearrangement - find lower priority items to move
            candidates_to_move = []
            
            for item_id, placed_item in placed_items.items():
                if (placed_item.priority < new_item.priority and 
                    placed_item.containerId):
                    candidates_to_move.append((placed_item, placed_item.priority))
            
            # Sort by priority (lowest first)
            candidates_to_move.sort(key=lambda x: x[1])
            
            # Try moving candidates until we find space
            for candidate_item, _ in candidates_to_move:
                # Temporarily remove item
                original_container = candidate_item.containerId
                original_position = candidate_item.position
                
                candidate_item.containerId = None
                candidate_item.position = None
                
                # Try to place new item in the freed space
                placement = self.find_optimal_placement(new_item, containers, placed_items)
                
                if placement:
                    # Found space! Add rearrangement step
                    rearrangement_steps.append({
                        "step": step_counter,
                        "action": "remove",
                        "itemId": candidate_item.itemId,
                        "fromContainer": original_container,
                        "fromPosition": original_position,
                        "toContainer": None,
                        "toPosition": None
                    })
                    step_counter += 1
                    
                    # Try to find new place for the moved item
                    new_placement = self.find_optimal_placement(candidate_item, containers, placed_items)
                    
                    if new_placement:
                        candidate_item.containerId = new_placement["containerId"]
                        candidate_item.position = new_placement["position"]
                        
                        rearrangement_steps.append({
                            "step": step_counter,
                            "action": "place",
                            "itemId": candidate_item.itemId,
                            "fromContainer": None,
                            "fromPosition": None,
                            "toContainer": new_placement["containerId"],
                            "toPosition": new_placement["position"]
                        })
                        step_counter += 1
                    
                    break
                else:
                    # Restore item placement
                    candidate_item.containerId = original_container
                    candidate_item.position = original_position
        
        return rearrangement_steps
