from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ValidationError
import re

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_item_id(item_id: str) -> str:
    """Validate and format item ID to 6-digit zero-padded format"""
    if not item_id:
        raise ValidationError("Item ID cannot be empty")
    
    # Remove any non-digit characters and pad to 6 digits
    digits_only = re.sub(r'\D', '', str(item_id))
    if not digits_only:
        raise ValidationError(f"Item ID must contain digits: {item_id}")
    
    return digits_only.zfill(6)

def validate_container_id(container_id: str) -> str:
    """Validate container ID format"""
    if not container_id or not isinstance(container_id, str):
        raise ValidationError("Container ID must be a non-empty string")
    
    if len(container_id.strip()) == 0:
        raise ValidationError("Container ID cannot be empty")
    
    return container_id.strip()

def validate_coordinates(position: Dict) -> bool:
    """Validate coordinate structure"""
    required_fields = ["startCoordinates", "endCoordinates"]
    coord_fields = ["width", "depth", "height"]
    
    for field in required_fields:
        if field not in position:
            raise ValidationError(f"Missing required field: {field}")
        
        if not isinstance(position[field], dict):
            raise ValidationError(f"{field} must be a dictionary")
        
        for coord_field in coord_fields:
            if coord_field not in position[field]:
                raise ValidationError(f"Missing coordinate field: {coord_field} in {field}")
            
            try:
                float(position[field][coord_field])
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid coordinate value for {coord_field} in {field}")
    
    # Check that end coordinates are greater than start coordinates
    start = position["startCoordinates"]
    end = position["endCoordinates"]
    
    for coord in coord_fields:
        if float(end[coord]) <= float(start[coord]):
            raise ValidationError(f"End coordinate {coord} must be greater than start coordinate")
    
    return True

def validate_priority(priority: Any) -> int:
    """Validate priority value"""
    try:
        priority_int = int(priority)
        if not (1 <= priority_int <= 100):
            raise ValidationError("Priority must be between 1 and 100")
        return priority_int
    except (ValueError, TypeError):
        raise ValidationError("Priority must be a valid integer")

def validate_dimensions(width: Any, depth: Any, height: Any) -> tuple:
    """Validate item dimensions"""
    try:
        w = float(width)
        d = float(depth)
        h = float(height)
        
        if w <= 0 or d <= 0 or h <= 0:
            raise ValidationError("All dimensions must be positive")
        
        return (w, d, h)
    except (ValueError, TypeError):
        raise ValidationError("Dimensions must be valid positive numbers")

def validate_mass(mass: Any) -> float:
    """Validate item mass"""
    try:
        mass_float = float(mass)
        if mass_float <= 0:
            raise ValidationError("Mass must be positive")
        return mass_float
    except (ValueError, TypeError):
        raise ValidationError("Mass must be a valid positive number")

def validate_usage_limit(usage_limit: Any) -> int:
    """Validate usage limit"""
    try:
        limit_int = int(usage_limit)
        if limit_int <= 0:
            raise ValidationError("Usage limit must be positive")
        return limit_int
    except (ValueError, TypeError):
        raise ValidationError("Usage limit must be a valid positive integer")

def validate_zone_name(zone: str) -> str:
    """Validate zone name"""
    if not zone or not isinstance(zone, str):
        raise ValidationError("Zone name must be a non-empty string")
    
    zone = zone.strip()
    if len(zone) == 0:
        raise ValidationError("Zone name cannot be empty")
    
    return zone

def validate_iso_date(date_string: str) -> bool:
    """Validate ISO date format"""
    if not date_string or date_string == "N/A":
        return True
    
    from datetime import datetime
    try:
        datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return True
    except ValueError:
        raise ValidationError(f"Invalid ISO date format: {date_string}")

def sanitize_csv_row(row: Dict) -> Dict:
    """Sanitize and validate CSV row data"""
    sanitized = {}
    
    for key, value in row.items():
        # Remove any extra whitespace
        if isinstance(value, str):
            value = value.strip()
        
        # Handle empty values
        if value == '' or value is None:
            if key in ['expiry_date']:
                value = 'N/A'
            else:
                raise ValidationError(f"Empty value for required field: {key}")
        
        sanitized[key] = value
    
    return sanitized
