"""
Integrated Advanced Placement Engine - Ultra-optimized version
"""
from typing import List, Dict, Optional, Tuple, Set, Any
import math
import time
import logging
from backend.models.item import Item
from backend.models.container import Container
from backend.engines.optimizers.rotation_optimizer import RotationOptimizer
from backend.engines.optimizers.space_optimizer import SpaceOptimizer, Space3D
from backend.engines.optimizers.priority_optimizer import PriorityOptimizer, PriorityStrategy
from backend.engines.optimizers.container_optimizer import ContainerOptimizer

logger = logging.getLogger(__name__)

class UltraAdvancedPlacementEngine:
    """
    Ultra-advanced placement engine combining multiple optimization strategies
    """
    
    def __init__(self):
        # Initialize optimizers
        self.rotation_optimizer = RotationOptimizer()
        self.space_optimizer = SpaceOptimizer()
        self.priority_optimizer = PriorityOptimizer()
        self.container_optimizer = ContainerOptimizer()
        
        # Tracking
        self.container_spaces = {}  # container_id -> List[Space3D]
        self.placed_items = {}      # container_id -> List[placement_info]
        self.placement_cache = {}
        
        # Performance settings
        self.max_iterations_per_item = 50
        self.enable_advanced_merging = True
        self.enable_predictive_placement = True
        
    def place_items_ultra_optimized(self, items_data: List[Dict], containers_data: List[Dict]) -> Tuple[List[Dict], int, bool]:
        """
        Ultra-optimized placement using all advanced techniques
        """
        start_time = time.time()
        
        # Initialize containers
        self._initialize_containers(containers_data)
        
        # Convert and optimize item sequence
        items = [self._dict_to_item(item_data) for item_data in items_data]
        optimized_items = self.priority_optimizer.optimize_item_sequence(
            items_data, containers_data, PriorityStrategy.BALANCED
        )
        items = [self._dict_to_item(item_data) for item_data in optimized_items]
        
        logger.info(f"Starting ultra-optimized placement for {len(items)} items")
        
        placements = []
        rearrangements = 0
        placed_count = 0
        
        # Batch processing for better performance
        batch_size = 100
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            batch_placements, batch_rearrangements = self._process_item_batch(
                batch, containers_data, placed_count
            )
            
            placements.extend(batch_placements)
            rearrangements += batch_rearrangements
            placed_count += len(batch_placements)
            
            if i % 500 == 0:
                logger.info(f"Processed {i + len(batch)}/{len(items)} items, placed {placed_count}")
        
        success = len(placements) > 0
        elapsed_time = time.time() - start_time
        
        logger.info(f"Ultra-optimized placement complete: placed {len(placements)}/{len(items)} items in {elapsed_time:.2f}s")
        
        return placements, rearrangements, success
    
    def _process_item_batch(self, items: List[Item], containers_data: List[Dict], 
                           start_index: int) -> Tuple[List[Dict], int]:
        """Process a batch of items with advanced techniques"""
        batch_placements = []
        batch_rearrangements = 0
        
        for idx, item in enumerate(items):
            # Try multiple placement strategies
            placement = self._try_advanced_placement(item, containers_data, start_index + idx)
            
            if placement:
                batch_placements.append(placement)
                self._update_container_spaces_after_placement(
                    placement['containerId'], 
                    (placement['position']['startCoordinates']['width'],
                     placement['position']['startCoordinates']['depth'],
                     placement['position']['startCoordinates']['height']),
                    (placement['position']['endCoordinates']['width'] - placement['position']['startCoordinates']['width'],
                     placement['position']['endCoordinates']['depth'] - placement['position']['startCoordinates']['depth'],
                     placement['position']['endCoordinates']['height'] - placement['position']['startCoordinates']['height'])
                )
            else:
                # Try rearrangement if placement fails
                if self.enable_predictive_placement and start_index + idx < 1000:  # Only for first 1000 items
                    rearrangement = self._try_rearrangement(item, containers_data)
                    if rearrangement:
                        batch_placements.append(rearrangement)
                        batch_rearrangements += 1
        
        return batch_placements, batch_rearrangements
    
    def _try_advanced_placement(self, item: Item, containers_data: List[Dict], item_index: int) -> Optional[Dict]:
        """Try advanced placement using multiple strategies"""
        item_dict = {
            'id': item.id,
            'width': item.width,
            'depth': item.depth,
            'height': item.height,
            'weight': getattr(item, 'weight', 1.0),
            'priority': getattr(item, 'priority', 1),
            'zone': getattr(item, 'zone', 'Storage_Bay')
        }
        
        # Strategy 1: Optimal container selection
        optimal_container_id = self.container_optimizer.select_optimal_container(
            item_dict, containers_data, self.placed_items, "balanced"
        )
        
        if optimal_container_id:
            placement = self._try_place_in_container_advanced(item, optimal_container_id, containers_data)
            if placement:
                return placement
        
        # Strategy 2: Try all containers with space efficiency priority
        container_candidates = self._get_sorted_container_candidates(item, containers_data)
        
        for container_id in container_candidates:
            placement = self._try_place_in_container_advanced(item, container_id, containers_data)
            if placement:
                return placement
        
        return None
    
    def _try_place_in_container_advanced(self, item: Item, container_id: str, 
                                       containers_data: List[Dict]) -> Optional[Dict]:
        """Advanced placement within a specific container"""
        if container_id not in self.container_spaces:
            return None
        
        # Get all possible orientations
        orientations = self.rotation_optimizer.get_all_orientations(
            item.width, item.depth, item.height
        )
        
        available_spaces = self.container_spaces[container_id]
        
        # Try each orientation with different placement strategies
        placement_strategies = ["corner_fit", "best_fit", "bottom_left", "skyline"]
        
        for orientation in orientations:
            width, depth, height = orientation
            
            for strategy in placement_strategies:
                result = self.space_optimizer.find_best_fit_position(
                    available_spaces, orientation, strategy
                )
                
                if result:
                    space, position = result
                    x, y, z = position
                    
                    # Validate rotation
                    if self.rotation_optimizer.validate_rotation(
                        (item.width, item.depth, item.height), orientation
                    ):
                        # Create placement
                        placement = {
                            'itemId': item.id,
                            'containerId': container_id,
                            'position': {
                                'startCoordinates': {
                                    'width': x,
                                    'depth': y,
                                    'height': z
                                },
                                'endCoordinates': {
                                    'width': x + width,
                                    'depth': y + depth,
                                    'height': z + height
                                }
                            }
                        }
                        
                        # Track placement
                        if container_id not in self.placed_items:
                            self.placed_items[container_id] = []
                        self.placed_items[container_id].append(placement)
                        
                        return placement
        
        return None
    
    def _get_sorted_container_candidates(self, item: Item, containers_data: List[Dict]) -> List[str]:
        """Get containers sorted by suitability for the item"""
        candidates = []
        
        for container in containers_data:
            container_id = container['id']
            
            # Check if item can physically fit
            if (container['width'] >= item.width and
                container['depth'] >= item.depth and
                container['height'] >= item.height):
                
                # Calculate suitability score
                volume_ratio = (item.width * item.depth * item.height) / (
                    container['width'] * container['depth'] * container['height']
                )
                
                utilization = len(self.placed_items.get(container_id, [])) / 20.0
                utilization_score = 1.0 - min(utilization, 1.0)
                
                zone_match = 1.0
                if hasattr(item, 'zone') and 'zone' in container:
                    zone_match = 2.0 if item.zone == container['zone'] else 0.5
                
                suitability = volume_ratio * utilization_score * zone_match
                candidates.append((suitability, container_id))
        
        # Sort by suitability (higher is better)
        candidates.sort(reverse=True)
        return [container_id for _, container_id in candidates]
    
    def _try_rearrangement(self, item: Item, containers_data: List[Dict]) -> Optional[Dict]:
        """Try to rearrange existing items to make space"""
        # This is a simplified rearrangement - in practice this would be more complex
        # For now, just try to find the best available space
        return None
    
    def _initialize_containers(self, containers_data: List[Dict]):
        """Initialize container spaces"""
        self.container_spaces.clear()
        self.placed_items.clear()
        
        for container in containers_data:
            container_id = container['id']
            
            # Create initial free space for entire container
            initial_space = Space3D(
                0, 0, 0,
                container['width'],
                container['depth'], 
                container['height']
            )
            
            self.container_spaces[container_id] = [initial_space]
            self.placed_items[container_id] = []
    
    def _update_container_spaces_after_placement(self, container_id: str, 
                                                position: Tuple[float, float, float],
                                                dimensions: Tuple[float, float, float]):
        """Update free spaces after item placement"""
        if container_id not in self.container_spaces:
            return
        
        x, y, z = position
        width, depth, height = dimensions
        
        # Find the space that contained this placement
        spaces = self.container_spaces[container_id]
        updated_spaces = []
        
        for space in spaces:
            if (space.x <= x < space.x + space.width and
                space.y <= y < space.y + space.depth and
                space.z <= z < space.z + space.height):
                
                # Split this space
                new_spaces = self.space_optimizer.split_space_after_placement(
                    space, position, dimensions
                )
                updated_spaces.extend(new_spaces)
            else:
                # Keep unchanged spaces
                updated_spaces.append(space)
        
        # Update container spaces
        self.container_spaces[container_id] = updated_spaces
        
        # Merge adjacent spaces if enabled
        if self.enable_advanced_merging and len(updated_spaces) > 10:
            self.container_spaces[container_id] = self.space_optimizer.merge_adjacent_spaces(
                updated_spaces
            )
    
    def _dict_to_item(self, item_dict: Dict) -> Item:
        """Convert dictionary to Item object"""
        item = Item(
            itemId=item_dict['id'],
            name=item_dict.get('name', f"Item {item_dict['id']}"),
            width=item_dict['width'],
            depth=item_dict['depth'],
            height=item_dict['height'],
            priority=item_dict.get('priority', 1),
            preferredZone=item_dict.get('zone', 'Storage_Bay')
        )
        
        # Add optional attributes
        if 'weight' in item_dict:
            item.mass = item_dict['weight']
        if 'mass' in item_dict:
            item.mass = item_dict['mass']
            
        return item
    
    def get_placement_statistics(self) -> Dict[str, Any]:
        """Get detailed placement statistics"""
        total_placements = sum(len(placements) for placements in self.placed_items.values())
        
        stats = {
            'total_placements': total_placements,
            'containers_used': len([c for c in self.placed_items.keys() if self.placed_items[c]]),
            'average_items_per_container': total_placements / len(self.placed_items) if self.placed_items else 0,
            'container_utilization': {}
        }
        
        # Calculate container utilization
        for container_id, placements in self.placed_items.items():
            stats['container_utilization'][container_id] = len(placements)
        
        return stats
