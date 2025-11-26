from typing import Dict, List, Optional
from datetime import datetime, timedelta
from backend.models.item import Item, ItemStatus

class SimulationEngine:
    """Handles time simulation and item state updates"""
    
    def __init__(self):
        self.current_simulation_date = datetime.now()
    
    def advance_time(self, num_days: int = 1, target_date: Optional[str] = None) -> datetime:
        """Advance simulation time by specified days or to target date"""
        if target_date:
            try:
                self.current_simulation_date = datetime.fromisoformat(target_date)
            except ValueError:
                raise ValueError(f"Invalid target date format: {target_date}")
        else:
            self.current_simulation_date += timedelta(days=num_days)
        
        return self.current_simulation_date
    
    def simulate_daily_usage(self, items_to_use: List[Dict], placed_items: Dict[str, Item]) -> Dict:
        """
        Simulate daily usage of items
        items_to_use: [{"itemId": "001", "name": "Food_Packet"}]
        """
        changes = {
            "itemsUsed": [],
            "itemsExpired": [],
            "itemsDepletedToday": []
        }
        
        # Process item usage
        for usage_request in items_to_use:
            item_id = usage_request.get("itemId")
            item_name = usage_request.get("name")
            
            # Find item by ID or name
            target_item = None
            
            if item_id and item_id in placed_items:
                target_item = placed_items[item_id]
            elif item_name:
                # Find first item with matching name that's still usable
                for item in placed_items.values():
                    if (item.name.lower() == item_name.lower() and 
                        not item.is_expired(self.current_simulation_date) and
                        not item.is_depleted()):
                        target_item = item
                        break
            
            if target_item:
                # Use the item
                original_uses = target_item.currentUses
                target_item.currentUses += 1
                
                changes["itemsUsed"].append({
                    "itemId": target_item.itemId,
                    "name": target_item.name,
                    "remainingUses": target_item.usageLimit - target_item.currentUses
                })
                
                # Check if item is now depleted
                if target_item.is_depleted():
                    changes["itemsDepletedToday"].append({
                        "itemId": target_item.itemId,
                        "name": target_item.name
                    })
        
        # Check for newly expired items
        for item in placed_items.values():
            if item.is_expired(self.current_simulation_date):
                # Check if it was not expired before today
                yesterday = self.current_simulation_date - timedelta(days=1)
                if not item.is_expired(yesterday):
                    changes["itemsExpired"].append({
                        "itemId": item.itemId,
                        "name": item.name
                    })
        
        return changes
    
    def get_current_date(self) -> datetime:
        """Get current simulation date"""
        return self.current_simulation_date
    
    def set_current_date(self, date: datetime):
        """Set current simulation date"""
        self.current_simulation_date = date
    
    def get_expiring_items(self, placed_items: Dict[str, Item], days_ahead: int = 7) -> List[Dict]:
        """Get items that will expire within specified days"""
        expiring_items = []
        cutoff_date = self.current_simulation_date + timedelta(days=days_ahead)
        
        for item in placed_items.values():
            if item.expiryDate and item.expiryDate != "N/A":
                try:
                    expiry_date = datetime.fromisoformat(item.expiryDate)
                    if self.current_simulation_date < expiry_date <= cutoff_date:
                        days_until_expiry = (expiry_date - self.current_simulation_date).days
                        expiring_items.append({
                            "itemId": item.itemId,
                            "name": item.name,
                            "expiryDate": item.expiryDate,
                            "daysUntilExpiry": days_until_expiry,
                            "containerId": item.containerId,
                            "priority": item.priority
                        })
                except ValueError:
                    continue
        
        # Sort by days until expiry (soonest first)
        expiring_items.sort(key=lambda x: x["daysUntilExpiry"])
        
        return expiring_items
    
    def get_low_usage_items(self, placed_items: Dict[str, Item], threshold: float = 0.8) -> List[Dict]:
        """Get items that are running low on uses"""
        low_usage_items = []
        
        for item in placed_items.values():
            if item.usageLimit > 0:
                usage_ratio = item.currentUses / item.usageLimit
                if usage_ratio >= threshold and not item.is_depleted():
                    remaining_uses = item.usageLimit - item.currentUses
                    low_usage_items.append({
                        "itemId": item.itemId,
                        "name": item.name,
                        "currentUses": item.currentUses,
                        "usageLimit": item.usageLimit,
                        "remainingUses": remaining_uses,
                        "usageRatio": usage_ratio,
                        "containerId": item.containerId,
                        "priority": item.priority
                    })
        
        # Sort by remaining uses (lowest first)
        low_usage_items.sort(key=lambda x: x["remainingUses"])
        
        return low_usage_items
    
    def get_item_statistics(self, placed_items: Dict[str, Item]) -> Dict:
        """Get comprehensive item statistics for current simulation state"""
        stats = {
            "totalItems": len(placed_items),
            "activeItems": 0,
            "expiredItems": 0,
            "depletedItems": 0,
            "itemsByZone": {},
            "itemsByPriority": {"high": 0, "medium": 0, "low": 0},
            "averageUsageRatio": 0.0,
            "totalMass": 0.0,
            "totalVolume": 0.0
        }
        
        total_usage_ratio = 0.0
        items_with_usage = 0
        
        for item in placed_items.values():
            status = item.get_status(self.current_simulation_date)
            
            if status == ItemStatus.ACTIVE:
                stats["activeItems"] += 1
            elif status == ItemStatus.EXPIRED:
                stats["expiredItems"] += 1
            elif status == ItemStatus.DEPLETED:
                stats["depletedItems"] += 1
            
            # Zone statistics
            zone = item.preferredZone
            if zone not in stats["itemsByZone"]:
                stats["itemsByZone"][zone] = 0
            stats["itemsByZone"][zone] += 1
            
            # Priority statistics
            if item.priority >= 80:
                stats["itemsByPriority"]["high"] += 1
            elif item.priority >= 50:
                stats["itemsByPriority"]["medium"] += 1
            else:
                stats["itemsByPriority"]["low"] += 1
            
            # Usage statistics
            if item.usageLimit > 0:
                usage_ratio = item.currentUses / item.usageLimit
                total_usage_ratio += usage_ratio
                items_with_usage += 1
            
            # Physical statistics
            stats["totalMass"] += item.mass
            stats["totalVolume"] += item.get_volume()
        
        if items_with_usage > 0:
            stats["averageUsageRatio"] = total_usage_ratio / items_with_usage
        
        return stats
    
    def predict_future_waste(self, placed_items: Dict[str, Item], days_ahead: int = 30) -> Dict:
        """Predict items that will become waste in the future"""
        future_date = self.current_simulation_date + timedelta(days=days_ahead)
        
        prediction = {
            "predictedWasteItems": [],
            "totalPredictedWaste": 0,
            "wasteByReason": {"expiry": 0, "depletion": 0},
            "wasteByZone": {}
        }
        
        for item in placed_items.values():
            will_be_waste = False
            reason = None
            
            # Check if will expire
            if item.expiryDate and item.expiryDate != "N/A":
                try:
                    expiry_date = datetime.fromisoformat(item.expiryDate)
                    if expiry_date <= future_date and not item.is_expired(self.current_simulation_date):
                        will_be_waste = True
                        reason = "expiry"
                except ValueError:
                    pass
            
            # For depletion prediction, we'd need usage patterns
            # Simplified: assume items with high usage ratio will deplete soon
            if not will_be_waste and item.usageLimit > 0:
                usage_ratio = item.currentUses / item.usageLimit
                if usage_ratio >= 0.9:  # Very close to depletion
                    will_be_waste = True
                    reason = "depletion"
            
            if will_be_waste:
                prediction["predictedWasteItems"].append({
                    "itemId": item.itemId,
                    "name": item.name,
                    "reason": reason,
                    "currentContainer": item.containerId,
                    "priority": item.priority
                })
                
                prediction["totalPredictedWaste"] += 1
                prediction["wasteByReason"][reason] += 1
                
                # Zone statistics
                zone = item.preferredZone
                if zone not in prediction["wasteByZone"]:
                    prediction["wasteByZone"][zone] = 0
                prediction["wasteByZone"][zone] += 1
        
        return prediction
