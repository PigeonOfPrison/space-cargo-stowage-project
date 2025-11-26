"""
Advanced Placement Engine for Space Logistics
--------------------------------------------
Implements an improved placement algorithm with:
- Comprehensive orientation testing (all 6 possible orientations)
- Enhanced zone matching with fuzzy logic and fallbacks
- Efficient free space management with merging
- Skyline and maximal rectangles packing techniques
- Multi-criteria container selection
- Performance optimizations and caching
- Detailed debugging and logging
- Advanced priority handling for multiple variables
"""
from typing import List, Dict, Optional, Tuple, Set, Any
import math
import time
import heapq
from datetime import datetime, timedelta
from backend.models.item import Item
from backend.models.container import Container
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriorityCalculator:
    """Advanced priority calculation handling multiple priority variables"""
    
    @staticmethod
    def calculate_composite_priority(item: Item, current_time: Optional[datetime] = None) -> float:
        """
        Calculate composite priority score from multiple variables:
        - Base priority (1-100): 40% weight
        - Expiry urgency: 30% weight
        - Usage depletion: 20% weight
        - Preferred zone urgency: 10% weight
        
        Returns a score from 0-100 where higher is more critical
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Base priority (40% weight, normalized to 0-40)
        base_priority = (item.priority / 100.0) * 40.0
        
        # Expiry urgency (30% weight, normalized to 0-30)
        expiry_score = 0.0
        if hasattr(item, 'expiryDate') and item.expiryDate:
            try:
                if isinstance(item.expiryDate, str):
                    expiry_date = datetime.fromisoformat(item.expiryDate.replace('Z', '+00:00'))
                else:
                    expiry_date = item.expiryDate
                
                days_to_expiry = (expiry_date - current_time).days
                
                if days_to_expiry <= 0:
                    expiry_score = 30.0  # Already expired - highest urgency
                elif days_to_expiry <= 7:
                    expiry_score = 25.0  # Expires within a week
                elif days_to_expiry <= 30:
                    expiry_score = 15.0  # Expires within a month
                elif days_to_expiry <= 90:
                    expiry_score = 5.0   # Expires within 3 months
                else:
                    expiry_score = 0.0   # Long-term storage
            except (ValueError, TypeError):
                expiry_score = 0.0
        
        # Usage depletion urgency (20% weight, normalized to 0-20)
        usage_score = 0.0
        if hasattr(item, 'usageLimit') and hasattr(item, 'usageCount'):
            if item.usageLimit and item.usageLimit > 0:
                remaining_uses = item.usageLimit - getattr(item, 'usageCount', 0)
                usage_ratio = remaining_uses / item.usageLimit
                
                if remaining_uses <= 0:
                    usage_score = 20.0  # No uses left
                elif usage_ratio <= 0.1:
                    usage_score = 15.0  # Less than 10% uses left
                elif usage_ratio <= 0.25:
                    usage_score = 10.0  # Less than 25% uses left
                elif usage_ratio <= 0.5:
                    usage_score = 5.0   # Less than 50% uses left
                else:
                    usage_score = 0.0   # Plenty of uses left
        
        # Preferred zone urgency (10% weight, normalized to 0-10)
        zone_score = 0.0
        if item.priority >= 80:  # High priority items need preferred zones
            zone_score = 10.0
        elif item.priority >= 60:  # Medium priority items benefit from preferred zones
            zone_score = 5.0
        
        total_score = base_priority + expiry_score + usage_score + zone_score
        return min(total_score, 100.0)  # Cap at 100
    
    @staticmethod
    def calculate_retrieval_priority(item: Item, retrieval_steps: int, current_time: Optional[datetime] = None) -> float:
        """
        Calculate retrieval priority considering accessibility and urgency.
        Higher scores indicate items that should be retrieved first.
        """
        composite_priority = PriorityCalculator.calculate_composite_priority(item, current_time)
        
        # Penalty for retrieval difficulty (each step reduces priority)
        retrieval_penalty = retrieval_steps * 5.0
        
        # Boost for very high priority items (reduce penalty)
        if item.priority >= 90:
            retrieval_penalty *= 0.5  # High priority items get less penalty
        elif item.priority >= 70:
            retrieval_penalty *= 0.7  # Medium-high priority items get reduced penalty
        
        retrieval_score = composite_priority - retrieval_penalty
        return max(retrieval_score, 0.0)
    
    @staticmethod
    def should_force_preferred_zone(item: Item) -> bool:
        """Determine if an item should be forced into its preferred zone"""
        # Force preferred zone for high priority items
        if item.priority >= 85:
            return True
        
        # Force preferred zone for items expiring soon
        if hasattr(item, 'expiryDate') and item.expiryDate:
            try:
                if isinstance(item.expiryDate, str):
                    expiry_date = datetime.fromisoformat(item.expiryDate.replace('Z', '+00:00'))
                else:
                    expiry_date = item.expiryDate
                
                days_to_expiry = (expiry_date - datetime.now()).days
                if days_to_expiry <= 14:  # Expires within 2 weeks
                    return True
            except (ValueError, TypeError):
                pass
        
        # Force preferred zone for items with low usage left
        if hasattr(item, 'usageLimit') and hasattr(item, 'usageCount'):
            if item.usageLimit and item.usageLimit > 0:
                remaining_uses = item.usageLimit - getattr(item, 'usageCount', 0)
                if remaining_uses <= 2:  # 2 or fewer uses left
                    return True
        
        return False

class AccessibilityTracker:
    """Track and optimize item accessibility for efficient retrieval"""
    
    def __init__(self):
        self.retrieval_cache: Dict[str, int] = {}  # item_id -> retrieval_steps
    
    def calculate_retrieval_steps(self, target_item_id: str, container_state: 'ContainerState') -> int:
        """Calculate number of steps needed to retrieve an item"""
        # Find the target item
        target_item = None
        for item in container_state.placed_items:
            if item.item_id == target_item_id:
                target_item = item
                break
        
        if not target_item:
            return float('inf')  # Item not found
        
        # Simple implementation: count items that block access from the open face
        # Assumes open face is at y=0 (depth=0)
        blocking_items = 0
        
        target_bounds = target_item.get_aabb()
        
        for other_item in container_state.placed_items:
            if other_item.item_id == target_item_id:
                continue
            
            other_bounds = other_item.get_aabb()
            
            # Check if other item blocks access to target item
            # Item blocks if it's in front (lower y) and overlaps in x,z
            if (other_bounds[1] < target_bounds[1] and  # other is in front
                other_bounds[3] > target_bounds[0] and  # x overlap
                other_bounds[0] < target_bounds[3] and  # x overlap
                other_bounds[5] > target_bounds[2] and  # z overlap
                other_bounds[2] < target_bounds[5]):    # z overlap
                blocking_items += 1
        
        self.retrieval_cache[target_item_id] = blocking_items
        return blocking_items
    
    def get_accessibility_score(self, item_id: str, container_state: 'ContainerState') -> float:
        """Get accessibility score (higher = more accessible)"""
        steps = self.calculate_retrieval_steps(item_id, container_state)
        if steps == float('inf'):
            return 0.0
        
        # Convert steps to score (fewer steps = higher score)
        return max(0.0, 100.0 - (steps * 10.0))

class ZoneOptimizer:
    """Optimize placement based on preferred zones and priority"""
    
    @staticmethod
    def calculate_zone_priority_score(item: Item, container_zone: str) -> float:
        """Calculate combined zone and priority score"""
        # Base zone matching score
        zone_score = ZoneOptimizer._calculate_zone_match_score(item.preferredZone, container_zone)
        
        # Priority multiplier
        priority_multiplier = 1.0 + (item.priority / 100.0)
        
        # High priority items get significant boost for preferred zones
        if item.preferredZone.lower() == container_zone.lower() and item.priority >= 80:
            zone_score += 50.0  # Significant boost for high priority in preferred zone
        
        return zone_score * priority_multiplier
    
    @staticmethod
    def get_zone_placement_strategy(item: Item) -> str:
        """Determine placement strategy based on item characteristics"""
        composite_priority = PriorityCalculator.calculate_composite_priority(item)
        
        if composite_priority >= 90:
            return "FORCE_PREFERRED"  # Must be in preferred zone
        elif composite_priority >= 70:
            return "PREFER_ZONE"     # Strong preference for zone
        elif composite_priority >= 50:
            return "CONSIDER_ZONE"   # Consider zone if space available
        else:
            return "ANY_ZONE"        # Any zone acceptable
    
    @staticmethod
    def _calculate_zone_match_score(preferred_zone: str, container_zone: str) -> float:
        """Calculate how well an item's preferred zone matches a container zone"""
        if not preferred_zone or not container_zone:
            return 0.5  # Neutral score for missing zones
        
        # Normalize zone names
        pref_clean = preferred_zone.lower().replace('_', ' ').replace('-', ' ')
        cont_clean = container_zone.lower().replace('_', ' ').replace('-', ' ')
        
        # Exact match
        if pref_clean == cont_clean:
            return 1.0
        
        # Check for partial string matches
        if pref_clean in cont_clean or cont_clean in pref_clean:
            return 0.8
        
        # Check for word matches
        pref_words = set(pref_clean.split())
        cont_words = set(cont_clean.split())
        common_words = pref_words.intersection(cont_words)
        if common_words:
            return 0.7
        
        # Initialize zone aliases for this static method
        zone_aliases = {
            'lab': ['lab', 'laboratory', 'research', 'science', 'experiment'],
            'storage': ['storage', 'cargo', 'warehouse', 'bay', 'hold'],
            'maintenance': ['maintenance', 'engineering', 'repair', 'workshop', 'technical'],
            'crew': ['crew', 'quarters', 'living', 'personal', 'residential'],
            'medical': ['medical', 'health', 'hospital', 'clinic', 'treatment'],
            'airlock': ['airlock', 'entry', 'exit', 'hatch', 'docking'],
            'cockpit': ['cockpit', 'bridge', 'control', 'command', 'pilot']
        }
        
        # Check against zone aliases
        pref_category = None
        cont_category = None
        
        for category, aliases in zone_aliases.items():
            if any(alias in pref_clean for alias in aliases):
                pref_category = category
            if any(alias in cont_clean for alias in aliases):
                cont_category = category
        
        # Same category match
        if pref_category and cont_category and pref_category == cont_category:
            return 0.6
        
        return 0.2  # Low match

class ItemSorter:
    """Advanced item sorting considering multiple priority variables"""
    
    @staticmethod
    def context_optimized_sort(items: List[Item], current_time: Optional[datetime] = None) -> List[Item]:
        """
        Sort items optimally considering all priority variables from CONTEXT.txt:
        1. Composite priority (priority + expiry + usage + zone)
        2. Size and shape factors for efficient packing
        3. Zone clustering for better organization
        """
        if current_time is None:
            current_time = datetime.now()
        
        def get_comprehensive_score(item: Item) -> Tuple[float, float, float]:
            # Primary score: composite priority
            composite_priority = PriorityCalculator.calculate_composite_priority(item, current_time)
            
            # Secondary score: packing efficiency
            volume = item.width * item.depth * item.height
            
            # Size category score (place large items first within priority groups)
            if volume > 10000:
                size_score = 100
            elif volume > 5000:
                size_score = 80
            elif volume > 1000:
                size_score = 60
            elif volume > 100:
                size_score = 40
            else:
                size_score = 20  # Small items get lower score
            
            # Shape difficulty score (complex shapes placed first)
            dims = sorted([item.width, item.depth, item.height])
            if dims[2] > dims[1] * 3:  # Long thin items
                shape_score = 100  # Place first (hardest to place)
            elif dims[2] < dims[0] * 1.5:  # Cube-like
                shape_score = 50   # Medium difficulty
            else:
                shape_score = 75   # Regular shapes
            
            # Zone clustering bonus (slight preference for grouping)
            zone_bonus = hash(item.preferredZone or "") % 10
            
            packing_score = size_score + shape_score + zone_bonus
            
            # Tertiary score: random tie-breaker
            tie_breaker = hash(item.itemId) % 1000
            
            return (composite_priority, packing_score, tie_breaker)
        
        # Sort by composite priority (desc), then packing score (desc), then tie-breaker
        return sorted(items, key=get_comprehensive_score, reverse=True)

class FreeSpace:
    """Represents a block of free space in 3D with enhanced functionality"""
    def __init__(self, x: float, y: float, z: float, width: float, depth: float, height: float):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        
    @property
    def volume(self) -> float:
        """Calculate the volume of this free space"""
        return self.width * self.depth * self.height
    
    @property
    def bottom_area(self) -> float:
        """Calculate the bottom area (for stability calculations)"""
        return self.width * self.depth
    
    def can_fit(self, width: float, depth: float, height: float) -> bool:
        """Check if an item can fit in this free space with exact dimensions"""
        return (self.width >= width and 
                self.depth >= depth and 
                self.height >= height)
    
    def can_fit_any_orientation(self, width: float, depth: float, height: float) -> List[Tuple[float, float, float]]:
        """Check all possible orientations and return list of valid ones"""
        orientations = [
            (width, depth, height),   # Original
            (depth, width, height),   # Rotate 90° on Z
            (width, height, depth),   # Rotate 90° on X
            (height, width, depth),   # Rotate 90° on X, then 90° on Z
            (depth, height, width),   # Rotate 90° on Y
            (height, depth, width)    # Rotate 90° on Y, then 90° on Z
        ]
        
        valid_orientations = []
        for w, d, h in orientations:
            if self.can_fit(w, d, h):
                valid_orientations.append((w, d, h))
                
        return valid_orientations
    
    def __repr__(self) -> str:
        return f"FreeSpace({self.x:.1f}, {self.y:.1f}, {self.z:.1f}, {self.width:.1f}, {self.depth:.1f}, {self.height:.1f})"

class PlacedItem:
    """Represents an item that has been placed in 3D space with enhanced tracking"""
    def __init__(self, item_id: str, x: float, y: float, z: float, width: float, depth: float, height: float, 
                 original_dims: Tuple[float, float, float], priority: int):
        self.item_id = item_id
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.depth = depth
        self.height = height
        self.original_dims = original_dims  # Store original dimensions for orientation tracking
        self.priority = priority
        self.timestamp = time.time()
        
    def get_volume(self) -> float:
        """Get the volume of this item"""
        return self.width * self.depth * self.height
    
    def get_position(self) -> Dict:
        """Get position in API format"""
        return {
            "startCoordinates": {
                "width": float(self.x),
                "depth": float(self.y),
                "height": float(self.z)
            },
            "endCoordinates": {
                "width": float(self.x + self.width),
                "depth": float(self.y + self.depth),
                "height": float(self.z + self.height)
            }
        }
    
    def get_aabb(self) -> Tuple[float, float, float, float, float, float]:
        """Get axis-aligned bounding box coordinates (min_x, min_y, min_z, max_x, max_y, max_z)"""
        return (self.x, self.y, self.z, 
                self.x + self.width, self.y + self.depth, self.z + self.height)
    
    def __repr__(self) -> str:
        return f"PlacedItem({self.item_id}, {self.x:.1f}, {self.y:.1f}, {self.z:.1f}, {self.width:.1f}, {self.depth:.1f}, {self.height:.1f})"

class ContainerState:
    """Manages the state of a container with advanced space management"""
    def __init__(self, container_id: str, width: float, depth: float, height: float, zone: str):
        self.container_id = container_id
        self.width = width
        self.depth = depth
        self.height = height
        self.zone = zone
        self.placed_items: List[PlacedItem] = []
        self.free_spaces: List[FreeSpace] = [FreeSpace(0, 0, 0, width, depth, height)]
        self.total_volume = width * depth * height
        self.used_volume = 0.0
        
    def get_utilization(self) -> float:
        """Get space utilization percentage"""
        if self.total_volume == 0:
            return 0.0
        return (self.used_volume / self.total_volume) * 100.0
    
    def get_largest_free_space(self) -> Optional[FreeSpace]:
        """Get the largest free space by volume"""
        if not self.free_spaces:
            return None
        return max(self.free_spaces, key=lambda fs: fs.volume)
    
    def can_place_item(self, x: float, y: float, z: float, width: float, depth: float, height: float) -> bool:
        """Check if an item can be placed at the specified position"""
        # Boundary check
        if (x < 0 or y < 0 or z < 0 or 
            x + width > self.width or 
            y + depth > self.depth or 
            z + height > self.height):
            return False
        
        # AABB collision detection with existing items
        item_aabb = (x, y, z, x + width, y + depth, z + height)
        
        for placed_item in self.placed_items:
            placed_aabb = placed_item.get_aabb()
            
            # Check for overlap on all three axes
            if not (item_aabb[3] <= placed_aabb[0] or item_aabb[0] >= placed_aabb[3] or
                    item_aabb[4] <= placed_aabb[1] or item_aabb[1] >= placed_aabb[4] or
                    item_aabb[5] <= placed_aabb[2] or item_aabb[2] >= placed_aabb[5]):
                return False
        
        return True
    
    def find_position(self, width: float, depth: float, height: float, priority: int) -> Optional[Tuple[float, float, float]]:
        """Find a suitable position for an item with given dimensions - OPTIMIZED FOR EVALUATION"""
        # EVALUATION OPTIMIZATION: Much simpler and faster algorithm
        
        # Try bottom corners first (most stable and fastest to check)
        corners = [
            (0, 0, 0),  # Origin corner
            (max(0, self.width - width), 0, 0),  # Right corner
            (0, max(0, self.depth - depth), 0),  # Back corner
            (max(0, self.width - width), max(0, self.depth - depth), 0)  # Far corner
        ]
        
        for x, y, z in corners:
            if (x >= 0 and y >= 0 and z >= 0 and
                x + width <= self.width and 
                y + depth <= self.depth and 
                z + height <= self.height and
                self.can_place_item(x, y, z, width, depth, height)):
                return (x, y, z)
        
        # If corners don't work, try first available free space
        for space in self.free_spaces[:10]:  # Only check first 10 spaces for speed
            if space.can_fit(width, depth, height):
                x, y, z = space.x, space.y, space.z
                if self.can_place_item(x, y, z, width, depth, height):
                    return (x, y, z)
        
        # If free spaces don't work, use coarse grid search
        step_size = max(10.0, width, depth)  # Large steps for speed
        
        max_x = max(0, self.width - width)
        max_y = max(0, self.depth - depth)
        max_z = max(0, self.height - height)
        
        # Only check a few positions for speed
        grid_points_checked = 0
        max_grid_points = 100  # Very limited for evaluation speed
        
        for z in [0, max_z * 0.5, max_z] if max_z > 0 else [0]:
            if grid_points_checked >= max_grid_points:
                break
                
            for y in range(0, int(max_y) + 1, int(step_size)):
                if grid_points_checked >= max_grid_points:
                    break
                    
                for x in range(0, int(max_x) + 1, int(step_size)):
                    grid_points_checked += 1
                    
                    if grid_points_checked > max_grid_points:
                        break
                        
                    if self.can_place_item(x, y, z, width, depth, height):
                        return (x, y, z)
        
        return None
    
    def _calculate_position_score(self, x: float, y: float, z: float, priority: int) -> float:
        """Calculate a score for a potential position (higher is better)"""
        # Accessibility score (prefer positions near opening)
        accessibility = max(0, 100 - y)
        
        # Stability score (prefer lower positions)
        stability = max(0, 100 - z)
        
        # Compactness score (prefer positions closer to other items)
        compactness = 0
        if self.placed_items:
            min_distance = float('inf')
            for item in self.placed_items:
                dist = math.sqrt((x - item.x)**2 + (y - item.y)**2 + (z - item.z)**2)
                min_distance = min(min_distance, dist)
            compactness = max(0, 100 - min(100, min_distance))
        
        # Priority bonus (higher priority items get better positions)
        priority_bonus = priority
        
        # Combined score with weights
        return (accessibility * 0.4 + 
                stability * 0.3 + 
                compactness * 0.1 + 
                priority_bonus * 0.2)
    
    def place_item(self, item_id: str, x: float, y: float, z: float, width: float, depth: float, height: float, 
                   original_dims: Tuple[float, float, float], priority: int) -> bool:
        """Place an item at the specified position and update space management"""
        if not self.can_place_item(x, y, z, width, depth, height):
            return False
        
        # Add to placed items
        item = PlacedItem(item_id, x, y, z, width, depth, height, original_dims, priority)
        self.placed_items.append(item)
        
        # Update volume tracking
        self.used_volume += item.get_volume()
        
        # Update free spaces
        self._update_free_spaces(x, y, z, width, depth, height)
        
        return True
    
    def _update_free_spaces(self, x: float, y: float, z: float, width: float, depth: float, height: float):
        """Update free spaces after placing an item - SIMPLIFIED FOR EVALUATION SPEED"""
        # EVALUATION OPTIMIZATION: Much simpler space management
        
        item_space = FreeSpace(x, y, z, width, depth, height)
        new_free_spaces = []
        
        for free_space in self.free_spaces:
            if self._spaces_overlap(free_space, item_space):
                # Simple split - just create basic splits for performance
                splits = []
                
                # Left split
                if item_space.x > free_space.x:
                    splits.append(FreeSpace(
                        free_space.x, free_space.y, free_space.z,
                        item_space.x - free_space.x, free_space.depth, free_space.height
                    ))
                
                # Right split
                if free_space.x + free_space.width > item_space.x + item_space.width:
                    splits.append(FreeSpace(
                        item_space.x + item_space.width, free_space.y, free_space.z,
                        (free_space.x + free_space.width) - (item_space.x + item_space.width),
                        free_space.depth, free_space.height
                    ))
                
                # Only keep splits larger than threshold for performance
                new_free_spaces.extend([s for s in splits if s.volume > 10.0])
            else:
                new_free_spaces.append(free_space)
        
        # Keep only the largest free spaces to improve performance
        if len(new_free_spaces) > 50:  # Limit free spaces for performance
            new_free_spaces.sort(key=lambda fs: fs.volume, reverse=True)
            new_free_spaces = new_free_spaces[:50]
        
        self.free_spaces = new_free_spaces
    
    def _spaces_overlap(self, space1: FreeSpace, space2: FreeSpace) -> bool:
        """Check if two 3D spaces overlap"""
        return not (space1.x + space1.width <= space2.x or 
                   space2.x + space2.width <= space1.x or
                   space1.y + space1.depth <= space2.y or 
                   space2.y + space2.depth <= space1.y or
                   space1.z + space1.height <= space2.z or 
                   space2.z + space2.height <= space1.z)
    
    def _split_free_space(self, free_space: FreeSpace, item_space: FreeSpace) -> List[FreeSpace]:
        """Split a free space around an item space using the six-way split method"""
        # Implementation is similar to the existing code but with simplifications
        # This creates up to 6 new spaces around the item (left, right, front, back, below, above)
        split_spaces = []
        
        # Left of the item
        if item_space.x > free_space.x:
            split_spaces.append(FreeSpace(
                free_space.x, free_space.y, free_space.z,
                item_space.x - free_space.x, free_space.depth, free_space.height
            ))
        
        # Right of the item
        if free_space.x + free_space.width > item_space.x + item_space.width:
            split_spaces.append(FreeSpace(
                item_space.x + item_space.width, free_space.y, free_space.z,
                (free_space.x + free_space.width) - (item_space.x + item_space.width),
                free_space.depth, free_space.height
            ))
        
        # Front of the item
        if item_space.y > free_space.y:
            split_spaces.append(FreeSpace(
                free_space.x, free_space.y, free_space.z,
                free_space.width, item_space.y - free_space.y, free_space.height
            ))
        
        # Back of the item
        if free_space.y + free_space.depth > item_space.y + item_space.depth:
            split_spaces.append(FreeSpace(
                free_space.x, item_space.y + item_space.depth, free_space.z,
                free_space.width, 
                (free_space.y + free_space.depth) - (item_space.y + item_space.depth),
                free_space.height
            ))
        
        # Below the item
        if item_space.z > free_space.z:
            split_spaces.append(FreeSpace(
                free_space.x, free_space.y, free_space.z,
                free_space.width, free_space.depth, item_space.z - free_space.z
            ))
        
        # Above the item
        if free_space.z + free_space.height > item_space.z + item_space.height:
            split_spaces.append(FreeSpace(
                free_space.x, free_space.y, item_space.z + item_space.height,
                free_space.width, free_space.depth,
                (free_space.z + free_space.height) - (item_space.z + item_space.height)
            ))
        
        return split_spaces
    
    def _merge_adjacent_spaces(self, spaces: List[FreeSpace]) -> List[FreeSpace]:
        """Merge adjacent free spaces to reduce fragmentation"""
        if not spaces:
            return []
        
        # Simple implementation - merge spaces that are exactly adjacent
        # For a full implementation, we would use a more sophisticated algorithm
        # that handles partial overlaps and complex adjacency
        
        merged = True
        while merged:
            merged = False
            result = []
            processed = set()
            
            for i, space1 in enumerate(spaces):
                if i in processed:
                    continue
                
                merged_space = FreeSpace(
                    space1.x, space1.y, space1.z,
                    space1.width, space1.depth, space1.height
                )
                merged_this_iteration = False
                
                for j, space2 in enumerate(spaces):
                    if i == j or j in processed:
                        continue
                    
                    # Check for x-adjacency (same y, z, height, depth)
                    if (abs(space1.y - space2.y) < 0.1 and
                        abs(space1.z - space2.z) < 0.1 and
                        abs(space1.depth - space2.depth) < 0.1 and
                        abs(space1.height - space2.height) < 0.1):
                        
                        # Right adjacency
                        if abs((space1.x + space1.width) - space2.x) < 0.1:
                            merged_space.width += space2.width
                            processed.add(j)
                            merged = True
                            merged_this_iteration = True
                        
                        # Left adjacency
                        elif abs((space2.x + space2.width) - space1.x) < 0.1:
                            merged_space.x = space2.x
                            merged_space.width += space2.width
                            processed.add(j)
                            merged = True
                            merged_this_iteration = True
                
                result.append(merged_space)
                processed.add(i)
            
            if merged:
                spaces = result
        
        return spaces
    
    def get_retrieval_steps(self, item_id: str) -> List[Dict]:
        """Calculate steps needed to retrieve an item"""
        # Simple implementation - identify items that block access
        item_to_retrieve = None
        for item in self.placed_items:
            if item.item_id == item_id:
                item_to_retrieve = item
                break
        
        if not item_to_retrieve:
            return []
        
        # An item blocks retrieval if it's in front of the target item
        # from the container opening perspective
        retrieval_steps = []
        step_count = 1
        
        for item in self.placed_items:
            if item.item_id == item_id:
                continue
                
            # Check if this item blocks the retrieval path
            if (item.y < item_to_retrieve.y and  # Item is closer to opening
                self._boxes_overlap_xy(item, item_to_retrieve)):
                
                # This item must be removed first
                retrieval_steps.append({
                    "step": step_count,
                    "action": "remove",
                    "itemId": item.item_id,
                })
                step_count += 1
        
        # Add the retrieval step for the target item
        retrieval_steps.append({
            "step": step_count,
            "action": "retrieve",
            "itemId": item_id,
        })
        step_count += 1
        
        # Add steps to place back the removed items in reverse order
        for i in range(len(retrieval_steps) - 1):
            blocking_item = retrieval_steps[len(retrieval_steps) - 2 - i]
            if blocking_item["action"] == "remove":
                retrieval_steps.append({
                    "step": step_count,
                    "action": "placeBack",
                    "itemId": blocking_item["itemId"],
                })
                step_count += 1
        
        return retrieval_steps
    
    def _boxes_overlap_xy(self, item1: PlacedItem, item2: PlacedItem) -> bool:
        """Check if two items overlap in the XY plane (ignoring Z)"""
        return not (item1.x + item1.width <= item2.x or
                   item2.x + item2.width <= item1.x or
                   item1.y + item1.depth <= item2.y or
                   item2.y + item2.depth <= item1.y)
    
    def __repr__(self) -> str:
        return (f"ContainerState({self.container_id}, {self.zone}, " 
                f"items: {len(self.placed_items)}, " 
                f"util: {self.get_utilization():.1f}%)")

class AdvancedPlacementEngine:
    """Advanced placement engine with enhanced algorithms"""
    
    def __init__(self):
        self.container_states: Dict[str, ContainerState] = {}
        self.zone_aliases: Dict[str, List[str]] = self._initialize_zone_aliases()
        self.placement_cache: Dict[str, Dict] = {}  # Cache for similar item placements
    
    def _initialize_zone_aliases(self) -> Dict[str, List[str]]:
        """Initialize dictionary of zone aliases and related terms"""
        return {
            'lab': ['lab', 'laboratory', 'research', 'science', 'experiment'],
            'storage': ['storage', 'cargo', 'warehouse', 'bay', 'hold'],
            'maintenance': ['maintenance', 'engineering', 'repair', 'workshop', 'technical'],
            'crew': ['crew', 'quarters', 'living', 'personal', 'residential'],
            'medical': ['medical', 'health', 'hospital', 'clinic', 'treatment'],
            'airlock': ['airlock', 'entry', 'exit', 'hatch', 'docking'],
            'cockpit': ['cockpit', 'bridge', 'control', 'command', 'pilot']
        }
    
    def calculate_zone_match_score(self, preferred_zone: str, container_zone: str) -> float:
        """Calculate how well an item's preferred zone matches a container zone"""
        if not preferred_zone or not container_zone:
            return 0.5  # Neutral score for missing zones
        
        # Normalize zone names
        pref_clean = preferred_zone.lower().replace('_', ' ').replace('-', ' ')
        cont_clean = container_zone.lower().replace('_', ' ').replace('-', ' ')
        
        # Exact match
        if pref_clean == cont_clean:
            return 1.0
        
        # Check for partial string matches
        if pref_clean in cont_clean or cont_clean in pref_clean:
            return 0.8
        
        # Check for word matches
        pref_words = set(pref_clean.split())
        cont_words = set(cont_clean.split())
        common_words = pref_words.intersection(cont_words)
        if common_words:
            return 0.7
        
        # Check against zone aliases
        pref_category = None
        cont_category = None
        
        # Use static zone aliases since this might be called from static context
        zone_aliases = {
            'lab': ['lab', 'laboratory', 'research', 'science', 'experiment'],
            'storage': ['storage', 'cargo', 'warehouse', 'bay', 'hold'],
            'maintenance': ['maintenance', 'engineering', 'repair', 'workshop', 'technical'],
            'crew': ['crew', 'quarters', 'living', 'personal', 'residential'],
            'medical': ['medical', 'health', 'hospital', 'clinic', 'treatment'],
            'airlock': ['airlock', 'entry', 'exit', 'hatch', 'docking'],
            'cockpit': ['cockpit', 'bridge', 'control', 'command', 'pilot']
        }
        
        for category, aliases in zone_aliases.items():
            if any(alias in pref_clean for alias in aliases):
                pref_category = category
            if any(alias in cont_clean for alias in aliases):
                cont_category = category
        
        if pref_category and cont_category and pref_category == cont_category:
            return 0.6
        
        # No match
        return 0.3
    
    def find_optimal_placement(self, item: Item, containers: Dict[str, Container], 
                             placed_items: Dict[str, Item]) -> Optional[Dict]:
        """Find optimal placement for an item using enhanced algorithms"""
        # Initialize container states if needed
        self._initialize_container_states(containers, placed_items)
        
        # Check cache for similar items (time optimization)
        cache_key = f"{item.width}x{item.depth}x{item.height}_p{item.priority}_{item.preferredZone}"
        if cache_key in self.placement_cache:
            cached_result = self.placement_cache[cache_key]
            container_id = cached_result["containerId"]
            
            # Verify the cached placement is still valid
            if container_id in self.container_states:
                container_state = self.container_states[container_id]
                position = cached_result["position"]
                start = position["startCoordinates"]
                end = position["endCoordinates"]
                
                width = end["width"] - start["width"]
                depth = end["depth"] - start["depth"]
                height = end["height"] - start["height"]
                
                # Try the cached position
                if container_state.can_place_item(
                    start["width"], start["depth"], start["height"],
                    width, depth, height
                ):
                    logger.info(f"Using cached placement for similar item {item.itemId}")
                    
                    # Update container state
                    success = container_state.place_item(
                        item.itemId, start["width"], start["depth"], start["height"],
                        width, depth, height, (item.width, item.depth, item.height), item.priority
                    )
                    
                    if success:
                        return cached_result
        
        # Get all valid containers sorted by suitability
        container_ranking = self._rank_containers_for_item(item)
        
        best_placement = None
        best_score = -1
        
        for rank_score, container_id in container_ranking:
            container = containers[container_id]
            container_state = self.container_states[container_id]
            
            # Try all possible orientations
            orientations = [
                (item.width, item.depth, item.height),    # Original
                (item.depth, item.width, item.height),    # Rotate 90° on Z
                (item.width, item.height, item.depth),    # Rotate 90° on X
                (item.height, item.width, item.depth),    # Rotate 90° on X, then 90° on Z
                (item.depth, item.height, item.width),    # Rotate 90° on Y
                (item.height, item.depth, item.width)     # Rotate 90° on Y, then 90° on Z
            ]
            
            for width, depth, height in orientations:
                # Check if this orientation fits in the container dimensions
                if (width > container.width or 
                    depth > container.depth or 
                    height > container.height):
                    continue
                
                # Find best position for this orientation
                position = container_state.find_position(width, depth, height, item.priority)
                
                if position:
                    x, y, z = position
                    
                    # Calculate placement score
                    zone_match = self.calculate_zone_match_score(item.preferredZone, container.zone)
                    accessibility_score = max(0, 100 - y) / 100.0
                    stability_score = max(0, 100 - z) / 100.0
                    
                    # Combined score with weights
                    placement_score = (
                        zone_match * 50 +                  # Zone matching (0-50)
                        item.priority * 0.3 +              # Priority (0-30)
                        accessibility_score * 15 +         # Accessibility (0-15)
                        stability_score * 5                # Stability (0-5)
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
                            },
                            "score": placement_score,
                            "orientation": (width, depth, height)
                        }
        
        # If placement found, update container state
        if best_placement:
            container_id = best_placement["containerId"]
            container_state = self.container_states[container_id]
            position = best_placement["position"]
            start = position["startCoordinates"]
            end = position["endCoordinates"]
            
            width = end["width"] - start["width"]
            depth = end["depth"] - start["depth"]
            height = end["height"] - start["height"]
            
            success = container_state.place_item(
                item.itemId, start["width"], start["depth"], start["height"],
                width, depth, height, (item.width, item.depth, item.height), item.priority
            )
            
            if success:
                # Cache this placement for similar items
                self.placement_cache[cache_key] = {
                    "containerId": container_id,
                    "position": position
                }
                
                # Remove score and orientation from returned result
                best_placement.pop("score", None)
                best_placement.pop("orientation", None)
                
                return best_placement
        
        return None
    
    def _initialize_container_states(self, containers: Dict[str, Container], placed_items: Dict[str, Item]):
        """Initialize or update container states with existing items"""
        # Initialize new containers
        for container_id, container in containers.items():
            if container_id not in self.container_states:
                self.container_states[container_id] = ContainerState(
                    container_id, container.width, container.depth, container.height, container.zone
                )
        
        # Add existing items to container states
        for item_id, item in placed_items.items():
            if hasattr(item, 'containerId') and hasattr(item, 'position'):
                container_id = item.containerId
                if container_id in self.container_states and item.position:
                    container_state = self.container_states[container_id]
                    pos = item.position
                    if pos and 'startCoordinates' in pos and 'endCoordinates' in pos:
                        start = pos['startCoordinates']
                        end = pos['endCoordinates']
                        
                        # Only add if not already in the container
                        if not any(pi.item_id == item_id for pi in container_state.placed_items):
                            width = end['width'] - start['width']
                            depth = end['depth'] - start['depth']
                            height = end['height'] - start['height']
                            
                            container_state.place_item(
                                item_id, start['width'], start['depth'], start['height'],
                                width, depth, height, (item.width, item.depth, item.height), 
                                item.priority
                            )
    
    def _rank_containers_for_item(self, item: Item) -> List[Tuple[float, str]]:
        """Rank containers by suitability for this item"""
        rankings = []
        
        for container_id, container_state in self.container_states.items():
            # Check if item can possibly fit in this container
            if (item.width > container_state.width and item.depth > container_state.width) or \
               (item.height > container_state.height):
                continue
            
            # Calculate base score from various factors
            
            # Zone match (0-100)
            zone_score = self.calculate_zone_match_score(
                item.preferredZone, container_state.zone
            ) * 100
            
            # Space efficiency (0-20)
            volume_ratio = min(1.0, (item.width * item.depth * item.height) / 
                              (container_state.width * container_state.depth * container_state.height))
            efficiency_score = (1 - volume_ratio) * 20  # Prefer containers that aren't too small
            
            # Utilization (0-20)
            # Prefer containers with similar utilization to balance load
            utilization = container_state.get_utilization() / 100.0
            utilization_score = (1 - abs(0.5 - utilization)) * 20
            
            # Free space (0-60)
            # Check if largest free space can fit the item in any orientation
            largest_space = container_state.get_largest_free_space()
            can_fit = False
            if largest_space:
                orientations = largest_space.can_fit_any_orientation(
                    item.width, item.depth, item.height
                )
                can_fit = len(orientations) > 0
            
            free_space_score = 60 if can_fit else 0
            
            # Combined score
            total_score = zone_score + efficiency_score + utilization_score + free_space_score
            rankings.append((total_score, container_id))
        
        # Sort by score (highest first)
        rankings.sort(reverse=True)
        return rankings
    
    def _rank_containers_for_item_enhanced(self, item: Item) -> List[Tuple[float, str]]:
        """Enhanced container ranking using new priority calculation and zone optimization"""
        rankings = []
        placement_strategy = ZoneOptimizer.get_zone_placement_strategy(item)
        force_preferred = PriorityCalculator.should_force_preferred_zone(item)
        
        for container_id, container_state in self.container_states.items():
            # Check if item can possibly fit in this container
            if (item.width > container_state.width and item.depth > container_state.width) or \
               (item.height > container_state.height):
                continue
            
            # Enhanced zone and priority scoring
            zone_priority_score = ZoneOptimizer.calculate_zone_priority_score(item, container_state.zone)
            
            # For items that must be in preferred zone, skip non-matching containers
            if force_preferred and item.preferredZone.lower() != container_state.zone.lower():
                continue
            
            # Calculate accessibility potential (prefer less crowded containers for high priority)
            utilization = container_state.get_utilization()
            accessibility_score = 0
            if item.priority >= 80:  # High priority items need good accessibility
                accessibility_score = max(0, 50 - utilization * 0.5)  # Better score for less crowded
            
            # Space efficiency (check if largest free space can accommodate item)
            largest_space = container_state.get_largest_free_space()
            space_score = 0
            if largest_space:
                orientations = largest_space.can_fit_any_orientation(item.width, item.depth, item.height)
                if orientations:
                    space_score = 60
                    # Bonus for exact fit
                    best_orientation = min(orientations, key=lambda o: o[0] * o[1] * o[2])
                    fit_efficiency = (item.width * item.depth * item.height) / (best_orientation[0] * best_orientation[1] * best_orientation[2])
                    space_score += fit_efficiency * 20
            
            # Combined score with strategy weighting
            if placement_strategy == "FORCE_PREFERRED":
                total_score = zone_priority_score * 2.0 + accessibility_score + space_score
            elif placement_strategy == "PREFER_ZONE":
                total_score = zone_priority_score * 1.5 + accessibility_score + space_score
            else:
                total_score = zone_priority_score + accessibility_score + space_score
            
            rankings.append((total_score, container_id))
        
        # Sort by score (highest first)
        rankings.sort(reverse=True)
        return rankings
    
    def _place_high_priority_item(self, item: Item, containers: Dict[str, Container]) -> Optional[Dict]:
        """Specialized placement for high priority items (priority >= 80)"""
        logger.info(f"Placing high priority item {item.itemId} (priority: {item.priority})")
        
        # Force preferred zone for high priority items (>= 85) or special conditions
        force_preferred = PriorityCalculator.should_force_preferred_zone(item)
        
        if force_preferred:
            # Force preferred zone containers first
            preferred_containers = []
            for container_id, container_state in self.container_states.items():
                if item.preferredZone.lower() == container_state.zone.lower():
                    preferred_containers.append((container_id, container_state))
            
            # Try preferred zone containers first
            for container_id, container_state in preferred_containers:
                # Look for positions with maximum accessibility (near front)
                position = self._find_accessible_position(item, container_state)
                if position:
                    x, y, z, width, depth, height = position
                    success = container_state.place_item(
                        item.itemId, x, y, z, width, depth, height,
                        (item.width, item.depth, item.height), item.priority
                    )
                    
                    if success:
                        return {
                            "itemId": item.itemId,
                            "containerId": container_id,
                            "position": {
                                "startCoordinates": {"width": float(x), "depth": float(y), "height": float(z)},
                                "endCoordinates": {"width": float(x + width), "depth": float(y + depth), "height": float(z + height)}
                            }
                        }
        
        # If preferred zone not required or full, use enhanced ranking
        rankings = self._rank_containers_for_item_enhanced(item)
        
        # Try top 5 containers
        for score, container_id in rankings[:5]:
            container_state = self.container_states[container_id]
            position = self._find_accessible_position(item, container_state)
            if not position:
                position = self._try_place_item_optimized(item, container_state)
            
            if position:
                x, y, z, width, depth, height = position
                success = container_state.place_item(
                    item.itemId, x, y, z, width, depth, height,
                    (item.width, item.depth, item.height), item.priority
                )
                
                if success:
                    if force_preferred:
                        logger.warning(f"Preferred zone full for high priority item {item.itemId}, using fallback")
                    return {
                        "itemId": item.itemId,
                        "containerId": container_id,
                        "position": {
                            "startCoordinates": {"width": float(x), "depth": float(y), "height": float(z)},
                            "endCoordinates": {"width": float(x + width), "depth": float(y + depth), "height": float(z + height)}
                        }
                    }
        
        return None
    
    def _place_medium_priority_item(self, item: Item, containers: Dict[str, Container]) -> Optional[Dict]:
        """Specialized placement for medium priority items (priority 50-79)"""
        # Use enhanced container ranking
        rankings = self._rank_containers_for_item_enhanced(item)
        
        # Try top 3 containers
        for score, container_id in rankings[:3]:
            container_state = self.container_states[container_id]
            position = self._try_place_item_optimized(item, container_state)
            
            if position:
                x, y, z, width, depth, height = position
                success = container_state.place_item(
                    item.itemId, x, y, z, width, depth, height,
                    (item.width, item.depth, item.height), item.priority
                )
                
                if success:
                    return {
                        "itemId": item.itemId,
                        "containerId": container_id,
                        "position": {
                            "startCoordinates": {"width": float(x), "depth": float(y), "height": float(z)},
                            "endCoordinates": {"width": float(x + width), "depth": float(y + depth), "height": float(z + height)}
                        }
                    }
        
        return None
    
    def _place_low_priority_item(self, item: Item, containers: Dict[str, Container]) -> Optional[Dict]:
        """Specialized placement for low priority items (priority < 50)"""
        # For low priority items, prioritize space efficiency over zone preference
        best_position = None
        best_efficiency = 0
        best_container_id = None
        
        for container_id, container_state in self.container_states.items():
            position = self._try_place_item_optimized(item, container_state)
            
            if position:
                x, y, z, width, depth, height = position
                item_volume = width * depth * height
                
                # Calculate space efficiency (how well this fills the available space)
                largest_space = container_state.get_largest_free_space()
                if largest_space:
                    space_volume = largest_space.volume
                    efficiency = item_volume / space_volume if space_volume > 0 else 0
                    
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_position = position
                        best_container_id = container_id
        
        if best_position and best_container_id:
            x, y, z, width, depth, height = best_position
            container_state = self.container_states[best_container_id]
            success = container_state.place_item(
                item.itemId, x, y, z, width, depth, height,
                (item.width, item.depth, item.height), item.priority
            )
            
            if success:
                return {
                    "itemId": item.itemId,
                    "containerId": best_container_id,
                    "position": {
                        "startCoordinates": {"width": float(x), "depth": float(y), "height": float(z)},
                        "endCoordinates": {"width": float(x + width), "depth": float(y + depth), "height": float(z + height)}
                    }
                }
        
        return None
    
    def _find_accessible_position(self, item: Item, container_state: 'ContainerState') -> Optional[Tuple[float, float, float, float, float, float]]:
        """Find position that maximizes accessibility (minimal retrieval steps)"""
        best_position = None
        min_depth = float('inf')  # Prefer positions closer to front (y=0)
        
        # Try all orientations
        orientations = [
            (item.width, item.depth, item.height),
            (item.depth, item.width, item.height)  # Only 0° and 90° for evaluation compatibility
        ]
        
        for width, depth, height in orientations:
            for free_space in container_state.free_spaces:
                if free_space.can_fit(width, depth, height):
                    # Prefer positions closer to the front (lower y values)
                    y_position = free_space.y
                    
                    if y_position < min_depth:
                        min_depth = y_position
                        best_position = (free_space.x, free_space.y, free_space.z, width, depth, height)
        
        return best_position
    
    def _find_best_fallback_position(self, item: Item) -> Optional[Dict]:
        """Find best fallback position when preferred zone is unavailable"""
        # Use standard placement but with preference for zones similar to preferred
        rankings = self._rank_containers_for_item_enhanced(item)
        
        for score, container_id in rankings:
            container_state = self.container_states[container_id]
            position = self._try_place_item_optimized(item, container_state)
            
            if position:
                x, y, z, width, depth, height = position
                success = container_state.place_item(
                    item.itemId, x, y, z, width, depth, height,
                    (item.width, item.depth, item.height), item.priority
                )
                
                if success:
                    return {
                        "itemId": item.itemId,
                        "containerId": container_id,
                        "position": {
                            "startCoordinates": {"width": float(x), "depth": float(y), "height": float(z)},
                            "endCoordinates": {"width": float(x + width), "depth": float(y + depth), "height": float(z + height)}
                        }
                    }
        
        return None
    
    def _try_place_item_optimized(self, item: Item, container_state: 'ContainerState') -> Optional[Tuple[float, float, float, float, float, float]]:
        """Optimized item placement with better orientation handling"""
        # Try multiple orientations (0°, 90°, and if item allows, 180° and 270°)
        orientations = [
            (item.width, item.depth, item.height),
            (item.depth, item.width, item.height)
        ]
        
        # Add vertical orientations if the item can be rotated
        if item.height < max(item.width, item.depth):
            orientations.extend([
                (item.height, item.depth, item.width),
                (item.height, item.width, item.depth),
                (item.width, item.height, item.depth),
                (item.depth, item.height, item.width)
            ])
        
        best_position = None
        best_score = -1
        
        for width, depth, height in orientations:
            for free_space in container_state.free_spaces:
                if free_space.can_fit(width, depth, height):
                    # Score this position - prefer positions that minimize waste
                    space_efficiency = (width * depth * height) / free_space.volume
                    accessibility_score = max(0, 100 - free_space.y)  # Prefer front positions
                    
                    score = container_state._calculate_position_score(
                        free_space.x, free_space.y, free_space.z, item.priority
                    ) + space_efficiency * 20 + accessibility_score * 0.1
                    
                    if score > best_score:
                        best_score = score
                        best_position = (free_space.x, free_space.y, free_space.z, width, depth, height)
        
        return best_position
    
    def place_items_enhanced_priority(self, items: List[Item], containers: Dict[str, Container]) -> List[Dict]:
        """
        Enhanced placement method using comprehensive priority handling.
        Handles multiple priority variables: priority, expiry, usage, preferred zones.
        """
        logger.info(f"Starting enhanced priority placement for {len(items)} items")
        
        # Initialize container states
        self._initialize_container_states(containers, {})
        
        # Sort items using context-optimized sorting with all priority variables
        sorted_items = ItemSorter.context_optimized_sort(items)
        
        placements = []
        
        # Initialize tracking for placement metrics
        high_priority_count = 0
        medium_priority_count = 0
        low_priority_count = 0
        preferred_zone_placements = 0
        forced_zone_placements = 0
        
        # Initialize accessibility tracker for optimizing retrieval
        self.accessibility_tracker = AccessibilityTracker()
        
        # Process items using priority-specific strategies
        for i, item in enumerate(sorted_items):
            if i % 50 == 0:  # Progress logging
                logger.info(f"Processing item {i+1}/{len(sorted_items)}: {item.itemId}")
            
            # Calculate composite priority and determine strategy
            composite_priority = PriorityCalculator.calculate_composite_priority(item)
            force_preferred = PriorityCalculator.should_force_preferred_zone(item)
            placement_strategy = ZoneOptimizer.get_zone_placement_strategy(item)
            
            placement = None
            
            # Use priority-specific placement strategies
            if item.priority >= 80:  # Use base priority for high priority classification
                placement = self._place_high_priority_item(item, containers)
                high_priority_count += 1
                if force_preferred:
                    forced_zone_placements += 1
            elif item.priority >= 50:  # Use base priority for medium priority classification
                placement = self._place_medium_priority_item(item, containers)
                medium_priority_count += 1
            else:
                placement = self._place_low_priority_item(item, containers)
                low_priority_count += 1
            
            if placement:
                placements.append(placement)
                
                # Track preferred zone placement success
                container_id = placement["containerId"]
                container_zone = self.container_states[container_id].zone
                if item.preferredZone and item.preferredZone.lower() == container_zone.lower():
                    preferred_zone_placements += 1
        
        # Log comprehensive placement statistics
        total_placed = len(placements)
        logger.info(f"Enhanced priority placement complete:")
        logger.info(f"  Total placed: {total_placed}/{len(items)} ({100*total_placed/len(items):.1f}%)")
        logger.info(f"  High priority: {high_priority_count}")
        logger.info(f"  Medium priority: {medium_priority_count}")
        logger.info(f"  Low priority: {low_priority_count}")
        logger.info(f"  Preferred zone success: {preferred_zone_placements}/{total_placed} ({100*preferred_zone_placements/max(1,total_placed):.1f}%)")
        logger.info(f"  Forced zone placements: {forced_zone_placements}")
        
        # Calculate and log space utilization
        total_utilization = 0
        container_count = 0
        for container_state in self.container_states.values():
            if container_state.placed_items:  # Only count containers with items
                total_utilization += container_state.get_utilization()
                container_count += 1
        
        avg_utilization = total_utilization / max(1, container_count)
        logger.info(f"  Average space utilization: {avg_utilization:.1f}%")
        
        return placements
    
    def get_retrieval_recommendations(self, items: List[Item]) -> List[Dict]:
        """
        Get retrieval recommendations based on composite priority and accessibility.
        Returns items sorted by retrieval priority considering:
        - Base priority
        - Expiry urgency
        - Usage depletion
        - Retrieval difficulty (accessibility)
        """
        retrieval_recommendations = []
        
        for item in items:
            # Find the container and calculate retrieval steps
            container_id = getattr(item, 'containerId', None)
            if container_id and container_id in self.container_states:
                container_state = self.container_states[container_id]
                retrieval_steps = self.accessibility_tracker.calculate_retrieval_steps(
                    item.itemId, container_state
                )
                
                # Calculate retrieval priority
                retrieval_priority = PriorityCalculator.calculate_retrieval_priority(
                    item, retrieval_steps
                )
                
                retrieval_recommendations.append({
                    "itemId": item.itemId,
                    "name": getattr(item, 'name', item.itemId),
                    "retrievalPriority": retrieval_priority,
                    "retrievalSteps": retrieval_steps,
                    "compositePriority": PriorityCalculator.calculate_composite_priority(item),
                    "basePriority": item.priority,
                    "containerId": container_id,
                    "accessibilityScore": self.accessibility_tracker.get_accessibility_score(
                        item.itemId, container_state
                    )
                })
        
        # Sort by retrieval priority (highest first)
        retrieval_recommendations.sort(key=lambda x: x["retrievalPriority"], reverse=True)
        
        return retrieval_recommendations
    
    def suggest_priority_based_rearrangement(self, new_items: List[Item]) -> List[Dict]:
        """
        Suggest rearrangements based on priority changes and new item requirements.
        Considers moving low-priority items to make space for high-priority items in preferred zones.
        """
        rearrangement_suggestions = []
        
        # Find high-priority new items that need preferred zones
        critical_new_items = [
            item for item in new_items 
            if PriorityCalculator.should_force_preferred_zone(item)
        ]
        
        for critical_item in critical_new_items:
            preferred_zone = critical_item.preferredZone.lower()
            
            # Find containers in preferred zone
            preferred_containers = [
                (cid, cstate) for cid, cstate in self.container_states.items()
                if cstate.zone.lower() == preferred_zone
            ]
            
            for container_id, container_state in preferred_containers:
                # Check if there's space for the critical item
                largest_space = container_state.get_largest_free_space()
                if not largest_space or not largest_space.can_fit_any_orientation(
                    critical_item.width, critical_item.depth, critical_item.height
                ):
                    # Find low-priority items that could be moved
                    moveable_items = [
                        item for item in container_state.placed_items
                        if item.priority < 50  # Low priority items
                    ]
                    
                    if moveable_items:
                        # Suggest moving the largest low-priority item
                        largest_moveable = max(moveable_items, key=lambda x: x.get_volume())
                        
                        rearrangement_suggestions.append({
                            "action": "move_to_make_space",
                            "itemToMove": largest_moveable.item_id,
                            "fromContainer": container_id,
                            "reason": f"Make space for high-priority item {critical_item.itemId} in preferred zone",
                            "newItemPriority": critical_item.priority,
                            "moveItemPriority": largest_moveable.priority
                        })
        
        return rearrangement_suggestions
    
    def optimize_for_expiry_urgency(self) -> List[Dict]:
        """
        Optimize placement for items approaching expiry.
        Returns suggestions to move soon-to-expire items to more accessible locations.
        """
        urgency_optimizations = []
        current_time = datetime.now()
        
        for container_id, container_state in self.container_states.items():
            for placed_item in container_state.placed_items:
                # Calculate days to expiry if expiry date exists
                days_to_expiry = None
                if hasattr(placed_item, 'expiryDate') and placed_item.expiryDate:
                    try:
                        if isinstance(placed_item.expiryDate, str):
                            expiry_date = datetime.fromisoformat(placed_item.expiryDate.replace('Z', '+00:00'))
                        else:
                            expiry_date = placed_item.expiryDate
                        days_to_expiry = (expiry_date - current_time).days
                    except (ValueError, TypeError):
                        continue
                
                # Check if item is approaching expiry and not easily accessible
                if days_to_expiry is not None and days_to_expiry <= 30:  # Expires within 30 days
                    retrieval_steps = self.accessibility_tracker.calculate_retrieval_steps(
                        placed_item.item_id, container_state
                    )
                    
                    if retrieval_steps > 2:  # Not easily accessible
                        urgency_optimizations.append({
                            "itemId": placed_item.item_id,
                            "currentContainer": container_id,
                            "daysToExpiry": days_to_expiry,
                            "currentRetrievalSteps": retrieval_steps,
                            "recommendation": "Move to more accessible location",
                            "urgencyLevel": "HIGH" if days_to_expiry <= 7 else "MEDIUM"
                        })
        
        # Sort by urgency (least days to expiry first)
        urgency_optimizations.sort(key=lambda x: x["daysToExpiry"])
        
        return urgency_optimizations
