"""
Simple, fast placement algorithm for space logistics
Self-contained with key improvements from archive analysis
"""
from typing import List, Dict, Optional, Tuple
from backend.models.item import Item
from backend.models.container import Container

class SimplePlacementEngine:
    """Fast placement engine with key improvements from archive algorithms"""
    
    def __init__(self):
        # Simple spatial grid cache for collision detection
        self.container_items: Dict[str, List[Dict]] = {}
        
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """
        Find optimal placement with improved algorithms
        Returns: {containerId: str, position: dict} or None
        """
        # Get valid orientations (PDF allows rotation)
        orientations = [
            (item.width, item.depth, item.height),  # Original
            (item.depth, item.width, item.height)   # 90° rotation
        ]
        
        # Sort containers by zone preference and space
        sorted_containers = self._sort_containers_smart(containers, item)
        
        for container in sorted_containers:
            container_id = container.containerId
            
            # Get existing items in this container
            existing_items = self._get_container_items(container_id, placed_items)
            
            # Try each orientation
            for width, depth, height in orientations:
                if not self._fits_in_container(width, depth, height, container):
                    continue
                
                # Find optimal position with accessibility optimization
                position = self._find_optimal_position(
                    width, depth, height, container, existing_items, item.priority
                )
                
                if position:
                    # Cache the placement
                    if container_id not in self.container_items:
                        self.container_items[container_id] = []
                    self.container_items[container_id].append({
                        'itemId': item.itemId,
                        'bounds': position
                    })
                    
                    return {
                        "containerId": container_id,
                        "position": position
                    }
        
        return None
    
    def _sort_containers_smart(self, containers: Dict[str, Container], item: Item) -> List[Container]:
        """Smart container sorting with zone matching and space optimization"""
        container_scores = []
        
        for container in containers.values():
            # Zone matching score (flexible)
            zone_score = self._calculate_zone_match(item.preferredZone, container.zone)
            
            # Space availability score
            space_score = (container.width * container.depth * container.height) / 1000000
            
            # Priority bonus for high-priority items in good zones
            priority_bonus = (item.priority / 100) * zone_score
            
            total_score = zone_score * 10 + space_score + priority_bonus
            container_scores.append((total_score, container))
        
        container_scores.sort(key=lambda x: x[0], reverse=True)
        return [container for score, container in container_scores]
    
    def _calculate_zone_match(self, preferred: str, container_zone: str) -> float:
        """Calculate flexible zone matching score"""
        pref_clean = preferred.lower().replace('_', '').replace(' ', '').replace('-', '')
        cont_clean = container_zone.lower().replace('_', '').replace(' ', '').replace('-', '')
        
        if pref_clean == cont_clean:
            return 3.0  # Exact match
        elif (pref_clean in cont_clean or cont_clean in pref_clean):
            return 2.0  # Partial match
        elif any(word in cont_clean for word in pref_clean.split() if len(word) > 2):
            return 1.5  # Word match
        else:
            return 1.0  # Any container
    
    def _fits_in_container(self, width: float, depth: float, height: float, 
                          container: Container) -> bool:
        """Check if item fits in container"""
        return (width <= container.width and 
                depth <= container.depth and 
                height <= container.height)
    
    def _get_container_items(self, container_id: str, placed_items: Dict[str, Item]) -> List[Dict]:
        """Get existing items in container with bounds"""
        items = []
        for item in placed_items.values():
            if (hasattr(item, 'containerId') and item.containerId == container_id and
                hasattr(item, 'position') and item.position):
                items.append({
                    'itemId': item.itemId,
                    'position': item.position
                })
        return items
    
    def _find_optimal_position(self, width: float, depth: float, height: float,
                             container: Container, existing_items: List[Dict], 
                             priority: int) -> Optional[Dict]:
        """Find optimal position with accessibility optimization"""
        
        # Generate candidate positions (prioritize accessibility)
        candidates = self._generate_smart_positions(
            width, depth, height, container, max_positions=25
        )
        
        best_position = None
        best_score = -1
        
        for x, y, z in candidates:
            # Check collision with existing items
            if not self._check_collision_fast(x, y, z, width, depth, height, existing_items):
                # Calculate position score (accessibility + priority optimization)
                score = self._calculate_position_score(x, y, z, container, priority)
                
                if score > best_score:
                    best_score = score
                    best_position = {
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
        
        return best_position
    
    def _generate_smart_positions(self, width: float, depth: float, height: float,
                                container: Container, max_positions: int = 25) -> List[Tuple[float, float, float]]:
        """Generate smart candidate positions prioritizing accessibility"""
        positions = []
        
        # Always try the most accessible position first (near opening)
        if (width <= container.width and depth <= container.depth and height <= container.height):
            positions.append((0.0, 0.0, 0.0))
        
        # Grid-based positions with accessibility priority
        grid_step = 15.0  # Balanced step size
        
        w_steps = min(int((container.width - width) / grid_step) + 1, 5)
        d_steps = min(int((container.depth - depth) / grid_step) + 1, 5)
        h_steps = min(int((container.height - height) / grid_step) + 1, 5)
        
        # Prioritize low depth (accessible) positions
        for d_idx in range(d_steps):
            for h_idx in range(h_steps):
                for w_idx in range(w_steps):
                    if len(positions) >= max_positions:
                        break
                    
                    x = w_idx * grid_step
                    y = d_idx * grid_step  # depth (accessibility factor)
                    z = h_idx * grid_step
                    
                    # Ensure within bounds
                    if (x + width <= container.width and
                        y + depth <= container.depth and
                        z + height <= container.height):
                        
                        pos = (float(x), float(y), float(z))
                        if pos not in positions:
                            positions.append(pos)
        
        return positions
    
    def _check_collision_fast(self, x: float, y: float, z: float,
                            width: float, depth: float, height: float,
                            existing_items: List[Dict]) -> bool:
        """Fast AABB collision detection"""
        x1, y1, z1 = x, y, z
        x2, y2, z2 = x + width, y + depth, z + height
        
        for item_data in existing_items:
            if 'position' not in item_data:
                continue
                
            try:
                pos = item_data['position']
                start = pos["startCoordinates"]
                end = pos["endCoordinates"]
                
                ex1, ey1, ez1 = start["width"], start["depth"], start["height"]
                ex2, ey2, ez2 = end["width"], end["depth"], end["height"]
                
                # AABB collision check
                if not (x2 <= ex1 or x1 >= ex2 or
                       y2 <= ey1 or y1 >= ey2 or
                       z2 <= ez1 or z1 >= ez2):
                    return True  # Collision detected
            except (KeyError, TypeError):
                continue
        
        return False  # No collision
    
    def _calculate_position_score(self, x: float, y: float, z: float,
                                container: Container, priority: int) -> float:
        """Calculate position score for accessibility optimization"""
        # Accessibility score (prefer positions near opening - low depth)
        accessibility_score = 1.0 - (y / container.depth)
        
        # Height accessibility (prefer lower positions)
        height_score = 1.0 - (z / container.height) * 0.3
        
        # Priority boost for high-priority items in accessible positions
        priority_bonus = (priority / 100.0) * accessibility_score * 0.5
        
        return accessibility_score + height_score + priority_bonus
    
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
            
            # Collision check
            existing_container_items = self._get_container_items(container.containerId, existing_items)
            if self._check_collision_fast(
                start["width"], start["depth"], start["height"],
                placed_width, placed_depth, placed_height,
                existing_container_items
            ):
                return False, "Collision with existing items"
            
            return True, "Valid placement"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def suggest_rearrangement(self, items: List[Item], containers: Dict[str, Container],
                            existing_items: Dict[str, Item]) -> List[Dict]:
        """Suggest rearrangement operations"""
        return []  # Simplified for now
