"""
Priority Optimizer - Smart priority and retrieval sequence optimization
"""
from typing import List, Dict, Tuple, Any, Optional
import math
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class PriorityStrategy(Enum):
    """Different priority optimization strategies"""
    CRITICAL_FIRST = "critical_first"
    SIZE_WEIGHT = "size_weight"
    ZONE_CLUSTERING = "zone_clustering"
    ACCESS_FREQUENCY = "access_frequency"
    BALANCED = "balanced"

class PriorityOptimizer:
    """Advanced priority optimization for item placement and retrieval"""
    
    def __init__(self):
        self.priority_cache = {}
        self.zone_priorities = {
            'Medical_Bay': 1.5,      # Highest priority for medical items
            'Life_Support': 1.4,     # Critical systems
            'Command_Center': 1.3,   # Control systems
            'Engineering_Bay': 1.2,  # Maintenance access
            'Cockpit': 1.1,         # Navigation systems
            'Storage_Bay': 1.0,     # Standard storage
            'Crew_Quarters': 0.9,   # Personal items
            'Lab': 0.8,             # Research items
            'Greenhouse': 0.7,      # Food production
            'Airlock': 0.6,         # EVA equipment
            'Maintenance_Bay': 0.5,  # Tools and spare parts
            'Sanitation_Bay': 0.4,  # Waste management
            'External_Storage': 0.3, # Long-term storage
            'Engine_Bay': 0.2,      # Engine components
            'Power_Bay': 0.1        # Power systems
        }
    
    def optimize_item_sequence(self, items: List[Dict[str, Any]], 
                              containers: List[Dict[str, Any]],
                              strategy: PriorityStrategy = PriorityStrategy.BALANCED) -> List[Dict[str, Any]]:
        """
        Optimize the order in which items should be placed
        """
        if strategy == PriorityStrategy.CRITICAL_FIRST:
            return self._critical_first_strategy(items)
        elif strategy == PriorityStrategy.SIZE_WEIGHT:
            return self._size_weight_strategy(items)
        elif strategy == PriorityStrategy.ZONE_CLUSTERING:
            return self._zone_clustering_strategy(items, containers)
        elif strategy == PriorityStrategy.ACCESS_FREQUENCY:
            return self._access_frequency_strategy(items)
        else:
            return self._balanced_strategy(items, containers)
    
    def _critical_first_strategy(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Place highest priority items first"""
        def priority_key(item):
            priority = item.get('priority', 1)
            # Invert because we want highest priority first
            return -priority
        
        return sorted(items, key=priority_key)
    
    def _size_weight_strategy(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Place larger/heavier items first for better stability"""
        def size_weight_key(item):
            volume = item.get('width', 0) * item.get('depth', 0) * item.get('height', 0)
            weight = item.get('weight', 0)
            # Combine volume and weight, prioritize larger items
            return -(volume + weight * 100)  # Weight has more impact
        
        return sorted(items, key=size_weight_key)
    
    def _zone_clustering_strategy(self, items: List[Dict[str, Any]], 
                                 containers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group items by their optimal zones to minimize container switching"""
        # Create zone groups
        zone_groups = {}
        container_zones = {c['id']: c.get('zone', 'Storage_Bay') for c in containers}
        
        for item in items:
            item_zone = item.get('zone', 'Storage_Bay')
            if item_zone not in zone_groups:
                zone_groups[item_zone] = []
            zone_groups[item_zone].append(item)
        
        # Sort zones by priority and items within zones by individual priority
        sorted_items = []
        for zone in sorted(zone_groups.keys(), 
                          key=lambda z: -self.zone_priorities.get(z, 0.5)):
            zone_items = sorted(zone_groups[zone], 
                              key=lambda item: -item.get('priority', 1))
            sorted_items.extend(zone_items)
        
        return sorted_items
    
    def _access_frequency_strategy(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize for retrieval frequency - place frequently accessed items accessibly"""
        def access_key(item):
            priority = item.get('priority', 1)
            # Estimate access frequency from priority and item type
            access_freq = priority
            
            # Boost certain item types that are accessed frequently
            item_type = item.get('type', '').lower()
            if any(freq_type in item_type for freq_type in 
                   ['medical', 'emergency', 'daily', 'tool', 'supply']):
                access_freq *= 1.5
            
            return -access_freq
        
        return sorted(items, key=access_key)
    
    def _balanced_strategy(self, items: List[Dict[str, Any]], 
                          containers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Balanced approach considering multiple factors"""
        def balanced_key(item):
            priority = item.get('priority', 1)
            volume = item.get('width', 0) * item.get('depth', 0) * item.get('height', 0)
            weight = item.get('weight', 0)
            zone = item.get('zone', 'Storage_Bay')
            
            # Multi-factor scoring
            priority_score = priority * 0.4
            size_score = (volume + weight * 10) * 0.3  # Larger items placed first
            zone_score = self.zone_priorities.get(zone, 0.5) * 0.3
            
            total_score = priority_score + size_score + zone_score
            return -total_score  # Negative for descending sort
        
        return sorted(items, key=balanced_key)
    
    def calculate_retrieval_efficiency(self, placements: List[Dict[str, Any]], 
                                     items: List[Dict[str, Any]]) -> float:
        """
        Calculate retrieval efficiency score based on placement accessibility
        """
        if not placements:
            return 0.0
        
        total_score = 0.0
        item_dict = {item['id']: item for item in items}
        
        for placement in placements:
            item_id = placement.get('itemId')
            if item_id not in item_dict:
                continue
                
            item = item_dict[item_id]
            priority = item.get('priority', 1)
            
            # Calculate accessibility score based on position
            position = placement.get('position', {})
            start_coords = position.get('startCoordinates', {})
            
            x = start_coords.get('width', 0)
            y = start_coords.get('depth', 0)
            z = start_coords.get('height', 0)
            
            # Items closer to entrance (x=0, y=0) and lower (z=0) are more accessible
            distance_penalty = math.sqrt(x*x + y*y) / 100.0
            height_penalty = z / 50.0
            accessibility = 1.0 / (1.0 + distance_penalty + height_penalty)
            
            # Weight by item priority
            item_score = accessibility * priority
            total_score += item_score
        
        # Normalize by number of placements and maximum possible priority
        max_possible_score = len(placements) * 5  # Assuming max priority is 5
        efficiency = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return min(efficiency, 100.0)  # Cap at 100%
    
    def suggest_rearrangements(self, placements: List[Dict[str, Any]], 
                              items: List[Dict[str, Any]],
                              containers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Suggest rearrangements to improve priority/retrieval efficiency
        """
        rearrangements = []
        item_dict = {item['id']: item for item in items}
        
        # Find high-priority items in poor positions
        for placement in placements:
            item_id = placement.get('itemId')
            if item_id not in item_dict:
                continue
                
            item = item_dict[item_id]
            priority = item.get('priority', 1)
            
            # If high priority item is placed poorly, suggest rearrangement
            if priority >= 4:  # High priority items
                position = placement.get('position', {})
                start_coords = position.get('startCoordinates', {})
                
                x = start_coords.get('width', 0)
                y = start_coords.get('depth', 0)
                z = start_coords.get('height', 0)
                
                # Check if item is in a hard-to-access position
                if x > 50 or y > 50 or z > 30:  # Arbitrary thresholds for "poor" position
                    rearrangement = {
                        'type': 'move_to_accessible',
                        'itemId': item_id,
                        'currentPosition': position,
                        'reason': f'High priority item (priority {priority}) in poor access position',
                        'suggestedZone': item.get('zone', 'Storage_Bay')
                    }
                    rearrangements.append(rearrangement)
        
        return rearrangements
    
    def calculate_priority_penalty(self, unplaced_items: List[Dict[str, Any]]) -> float:
        """Calculate penalty for unplaced items based on their priorities"""
        if not unplaced_items:
            return 0.0
        
        total_penalty = 0.0
        for item in unplaced_items:
            priority = item.get('priority', 1)
            # Higher priority items incur larger penalties
            penalty = priority * priority  # Quadratic penalty
            total_penalty += penalty
        
        # Normalize by number of items and max penalty per item
        max_penalty_per_item = 25  # 5^2 for max priority
        max_total_penalty = len(unplaced_items) * max_penalty_per_item
        
        penalty_percentage = (total_penalty / max_total_penalty) * 100 if max_total_penalty > 0 else 0
        return min(penalty_percentage, 100.0)
