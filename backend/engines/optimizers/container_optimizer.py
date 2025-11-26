"""
Container Optimizer - Smart container selection and load balancing
"""
from typing import List, Dict, Tuple, Optional, Any
import math
import logging

logger = logging.getLogger(__name__)

class ContainerOptimizer:
    """Advanced container selection and optimization"""
    
    def __init__(self):
        self.container_cache = {}
        self.load_balance_threshold = 0.8  # 80% utilization threshold
        
    def select_optimal_container(self, item: Dict[str, Any], 
                                containers: List[Dict[str, Any]],
                                current_placements: Dict[str, List[Dict[str, Any]]],
                                strategy: str = "balanced") -> Optional[str]:
        """
        Select the optimal container for an item using various strategies
        """
        item_width = item.get('width', 0)
        item_depth = item.get('depth', 0)  
        item_height = item.get('height', 0)
        item_zone = item.get('zone', 'Storage_Bay')
        item_priority = item.get('priority', 1)
        
        # Filter containers that can physically fit the item
        fitting_containers = []
        for container in containers:
            if (container.get('width', 0) >= item_width and
                container.get('depth', 0) >= item_depth and
                container.get('height', 0) >= item_height):
                fitting_containers.append(container)
        
        if not fitting_containers:
            return None
        
        if strategy == "zone_priority":
            return self._zone_priority_selection(item, fitting_containers, current_placements)
        elif strategy == "load_balance":
            return self._load_balance_selection(item, fitting_containers, current_placements)
        elif strategy == "space_efficiency":
            return self._space_efficiency_selection(item, fitting_containers, current_placements)
        elif strategy == "accessibility":
            return self._accessibility_selection(item, fitting_containers, current_placements)
        else:
            return self._balanced_selection(item, fitting_containers, current_placements)
    
    def _zone_priority_selection(self, item: Dict[str, Any], 
                                containers: List[Dict[str, Any]],
                                current_placements: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Select container based on zone matching"""
        item_zone = item.get('zone', 'Storage_Bay')
        
        # Score containers by zone match
        scored_containers = []
        for container in containers:
            container_zone = container.get('zone', 'Storage_Bay')
            container_id = container['id']
            
            # Perfect zone match gets highest score
            if container_zone == item_zone:
                zone_score = 10
            # Similar zones get partial credit
            elif self._zones_compatible(item_zone, container_zone):
                zone_score = 5
            else:
                zone_score = 1
            
            # Consider current utilization
            utilization = self._calculate_container_utilization(container_id, current_placements)
            utilization_score = 5 - (utilization * 5)  # Prefer less utilized containers
            
            total_score = zone_score + utilization_score
            scored_containers.append((total_score, container_id))
        
        # Return container with highest score
        if scored_containers:
            scored_containers.sort(reverse=True)
            return scored_containers[0][1]
        
        return None
    
    def _load_balance_selection(self, item: Dict[str, Any], 
                               containers: List[Dict[str, Any]],
                               current_placements: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Select container to balance load across containers"""
        # Find container with lowest utilization
        min_utilization = float('inf')
        best_container = None
        
        for container in containers:
            container_id = container['id']
            utilization = self._calculate_container_utilization(container_id, current_placements)
            
            if utilization < min_utilization:
                min_utilization = utilization
                best_container = container_id
        
        return best_container
    
    def _space_efficiency_selection(self, item: Dict[str, Any], 
                                   containers: List[Dict[str, Any]],
                                   current_placements: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Select container for maximum space efficiency"""
        item_volume = item.get('width', 0) * item.get('depth', 0) * item.get('height', 0)
        
        best_container = None
        min_waste = float('inf')
        
        for container in containers:
            container_volume = (container.get('width', 0) * 
                              container.get('depth', 0) * 
                              container.get('height', 0))
            
            # Calculate available volume
            container_id = container['id']
            used_volume = self._calculate_used_volume(container_id, current_placements)
            available_volume = container_volume - used_volume
            
            # Calculate waste if item is placed here
            if available_volume >= item_volume:
                waste = available_volume - item_volume
                if waste < min_waste:
                    min_waste = waste
                    best_container = container_id
        
        return best_container
    
    def _accessibility_selection(self, item: Dict[str, Any], 
                                containers: List[Dict[str, Any]],
                                current_placements: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Select container based on item accessibility needs"""
        item_priority = item.get('priority', 1)
        
        # High priority items need accessible containers
        accessibility_scores = []
        for container in containers:
            container_id = container['id']
            zone = container.get('zone', 'Storage_Bay')
            
            # Score based on zone accessibility
            accessibility_score = self._get_zone_accessibility_score(zone)
            
            # Adjust for current container fullness
            utilization = self._calculate_container_utilization(container_id, current_placements)
            if utilization > 0.7:  # Penalize overly full containers
                accessibility_score *= (1 - utilization)
            
            accessibility_scores.append((accessibility_score, container_id))
        
        # For high priority items, choose most accessible
        # For low priority items, choose least accessible to save space
        if item_priority >= 4:
            accessibility_scores.sort(reverse=True)
        else:
            accessibility_scores.sort()
        
        if accessibility_scores:
            return accessibility_scores[0][1]
        
        return None
    
    def _balanced_selection(self, item: Dict[str, Any], 
                           containers: List[Dict[str, Any]],
                           current_placements: Dict[str, List[Dict[str, Any]]]) -> Optional[str]:
        """Balanced selection considering multiple factors"""
        item_zone = item.get('zone', 'Storage_Bay')
        item_priority = item.get('priority', 1)
        item_volume = item.get('width', 0) * item.get('depth', 0) * item.get('height', 0)
        
        scored_containers = []
        for container in containers:
            container_id = container['id']
            container_zone = container.get('zone', 'Storage_Bay')
            
            # Zone matching score (30% weight)
            if container_zone == item_zone:
                zone_score = 10
            elif self._zones_compatible(item_zone, container_zone):
                zone_score = 6
            else:
                zone_score = 2
            
            # Load balancing score (25% weight)
            utilization = self._calculate_container_utilization(container_id, current_placements)
            load_score = 10 * (1 - utilization)
            
            # Space efficiency score (25% weight)
            container_volume = (container.get('width', 0) * 
                              container.get('depth', 0) * 
                              container.get('height', 0))
            used_volume = self._calculate_used_volume(container_id, current_placements)
            available_volume = container_volume - used_volume
            
            if available_volume > 0:
                efficiency = item_volume / available_volume
                space_score = min(10, efficiency * 10)
            else:
                space_score = 0
            
            # Accessibility score (20% weight)
            accessibility_score = self._get_zone_accessibility_score(container_zone)
            if item_priority >= 4:  # High priority items need good access
                accessibility_score *= 1.5
            
            # Weighted total score
            total_score = (zone_score * 0.3 + 
                          load_score * 0.25 + 
                          space_score * 0.25 + 
                          accessibility_score * 0.2)
            
            scored_containers.append((total_score, container_id))
        
        if scored_containers:
            scored_containers.sort(reverse=True)
            return scored_containers[0][1]
        
        return None
    
    def _zones_compatible(self, zone1: str, zone2: str) -> bool:
        """Check if two zones are compatible for cross-placement"""
        compatible_groups = [
            ['Medical_Bay', 'Life_Support'],
            ['Command_Center', 'Cockpit'],
            ['Engineering_Bay', 'Maintenance_Bay', 'Power_Bay'],
            ['Storage_Bay', 'External_Storage'],
            ['Crew_Quarters', 'Sanitation_Bay'],
            ['Lab', 'Greenhouse']
        ]
        
        for group in compatible_groups:
            if zone1 in group and zone2 in group:
                return True
        
        return False
    
    def _calculate_container_utilization(self, container_id: str, 
                                       current_placements: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate current utilization percentage of a container"""
        if container_id not in current_placements:
            return 0.0
        
        # This is a simplified calculation - in practice you'd need container dimensions
        # and placed item volumes
        placements = current_placements[container_id]
        return min(len(placements) / 20.0, 1.0)  # Assume max 20 items per container
    
    def _calculate_used_volume(self, container_id: str, 
                              current_placements: Dict[str, List[Dict[str, Any]]]) -> float:
        """Calculate used volume in a container"""
        if container_id not in current_placements:
            return 0.0
        
        # This would need actual item dimensions from placements
        # Simplified for now
        placements = current_placements[container_id]
        return len(placements) * 1000  # Assume 1000 cubic units per item
    
    def _get_zone_accessibility_score(self, zone: str) -> float:
        """Get accessibility score for a zone"""
        accessibility_scores = {
            'Medical_Bay': 10,      # Most accessible
            'Command_Center': 9,
            'Cockpit': 8,
            'Life_Support': 7,
            'Engineering_Bay': 6,
            'Storage_Bay': 5,
            'Lab': 4,
            'Crew_Quarters': 3,
            'Maintenance_Bay': 2,
            'External_Storage': 1,  # Least accessible
            'Engine_Bay': 1,
            'Power_Bay': 1,
            'Greenhouse': 2,
            'Airlock': 3,
            'Sanitation_Bay': 2
        }
        
        return accessibility_scores.get(zone, 5)
    
    def optimize_container_distribution(self, placements: Dict[str, List[Dict[str, Any]]], 
                                      containers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and optimize container distribution"""
        analysis = {
            'utilization_by_container': {},
            'zone_distribution': {},
            'load_balance_score': 0.0,
            'recommendations': []
        }
        
        # Calculate utilization by container
        total_utilization = 0
        container_count = len(containers)
        
        for container in containers:
            container_id = container['id']
            utilization = self._calculate_container_utilization(container_id, placements)
            analysis['utilization_by_container'][container_id] = utilization
            total_utilization += utilization
        
        # Calculate load balance score
        if container_count > 0:
            avg_utilization = total_utilization / container_count
            variance = sum((util - avg_utilization) ** 2 
                          for util in analysis['utilization_by_container'].values()) / container_count
            
            # Lower variance = better load balance
            analysis['load_balance_score'] = max(0, 100 - (variance * 100))
        
        # Zone distribution analysis
        zone_counts = {}
        for container_id, container_placements in placements.items():
            container = next((c for c in containers if c['id'] == container_id), None)
            if container:
                zone = container.get('zone', 'Storage_Bay')
                zone_counts[zone] = zone_counts.get(zone, 0) + len(container_placements)
        
        analysis['zone_distribution'] = zone_counts
        
        # Generate recommendations
        for container_id, utilization in analysis['utilization_by_container'].items():
            if utilization > 0.9:
                analysis['recommendations'].append(
                    f"Container {container_id} is overutilized ({utilization:.1%})"
                )
            elif utilization < 0.1:
                analysis['recommendations'].append(
                    f"Container {container_id} is underutilized ({utilization:.1%})"
                )
        
        return analysis
