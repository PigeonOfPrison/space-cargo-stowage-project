import csv
import io
from typing import List, Dict, Tuple, Optional
from backend.models.item import Item
from backend.models.container import Container
from backend.utils.validators import (
    validate_item_id, validate_container_id, validate_coordinates,
    validate_priority, validate_dimensions, validate_mass,
    validate_usage_limit, validate_zone_name, validate_iso_date,
    sanitize_csv_row, ValidationError
)

class CSVHandler:
    """Handles CSV import/export operations"""
    
    def __init__(self):
        self.required_item_fields = [
            'item_id', 'name', 'width_cm', 'depth_cm', 'height_cm', 
            'mass_kg', 'priority', 'expiry_date', 'usage_limit', 'preferred_zone'
        ]
        
        self.required_container_fields = [
            'container_id', 'zone', 'width_cm', 'depth_cm', 'height_cm'
        ]
    
    def parse_items_csv(self, csv_content: str) -> Tuple[List[Item], List[Dict]]:
        """
        Parse CSV content and return list of Item objects and any errors
        Returns: (items_list, errors_list)
        """
        items = []
        errors = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    # Sanitize row data
                    clean_row = sanitize_csv_row(row)
                    
                    # Validate required fields
                    missing_fields = [field for field in self.required_item_fields 
                                    if field not in clean_row]
                    if missing_fields:
                        errors.append({
                            "row": row_num,
                            "message": f"Missing required fields: {', '.join(missing_fields)}"
                        })
                        continue
                    
                    # Create and validate item
                    item = self._create_item_from_row(clean_row, row_num)
                    if item:
                        items.append(item)
                        
                except ValidationError as e:
                    errors.append({
                        "row": row_num,
                        "message": str(e)
                    })
                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "message": f"Unexpected error: {str(e)}"
                    })
        
        except Exception as e:
            errors.append({
                "row": 1,
                "message": f"CSV parsing error: {str(e)}"
            })
        
        return items, errors
    
    def _create_item_from_row(self, row: Dict, row_num: int) -> Optional[Item]:
        """Create Item object from CSV row"""
        try:
            # Validate and format item ID
            item_id = validate_item_id(row['item_id'])
            
            # Validate dimensions
            width, depth, height = validate_dimensions(
                row['width_cm'], row['depth_cm'], row['height_cm']
            )
            
            # Validate mass
            mass = validate_mass(row['mass_kg'])
            
            # Validate priority
            priority = validate_priority(row['priority'])
            
            # Validate usage limit
            usage_limit = validate_usage_limit(row['usage_limit'])
            
            # Validate zone
            preferred_zone = validate_zone_name(row['preferred_zone'])
            
            # Validate expiry date
            expiry_date = row['expiry_date']
            if expiry_date and expiry_date != 'N/A':
                validate_iso_date(expiry_date)
            else:
                expiry_date = None
            
            # Create item
            return Item(
                itemId=item_id,
                name=str(row['name']).strip(),
                width=width,
                depth=depth,
                height=height,
                mass=mass,
                priority=priority,
                expiryDate=expiry_date,
                usageLimit=usage_limit,
                preferredZone=preferred_zone
            )
            
        except ValidationError as e:
            raise ValidationError(f"Row {row_num}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Row {row_num}: Unexpected error - {str(e)}")
    
    def parse_containers_csv(self, csv_content: str) -> Tuple[List[Container], List[Dict]]:
        """
        Parse CSV content and return list of Container objects and any errors
        Returns: (containers_list, errors_list)
        """
        containers = []
        errors = []
        
        try:
            # Parse CSV content
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    # Sanitize row data
                    clean_row = sanitize_csv_row(row)
                    
                    # Validate required fields
                    missing_fields = [field for field in self.required_container_fields 
                                    if field not in clean_row]
                    if missing_fields:
                        errors.append({
                            "row": row_num,
                            "message": f"Missing required fields: {', '.join(missing_fields)}"
                        })
                        continue
                    
                    # Create and validate container
                    container = self._create_container_from_row(clean_row, row_num)
                    if container:
                        containers.append(container)
                        
                except ValidationError as e:
                    errors.append({
                        "row": row_num,
                        "message": str(e)
                    })
                except Exception as e:
                    errors.append({
                        "row": row_num,
                        "message": f"Unexpected error: {str(e)}"
                    })
        
        except Exception as e:
            errors.append({
                "row": 1,
                "message": f"CSV parsing error: {str(e)}"
            })
        
        return containers, errors
    
    def _create_container_from_row(self, row: Dict, row_num: int) -> Optional[Container]:
        """Create Container object from CSV row"""
        try:
            # Validate container ID
            container_id = validate_container_id(row['container_id'])
            
            # Validate zone
            zone = validate_zone_name(row['zone'])
            
            # Validate dimensions
            width, depth, height = validate_dimensions(
                row['width_cm'], row['depth_cm'], row['height_cm']
            )
            
            # Create container
            return Container(
                containerId=container_id,
                zone=zone,
                width=width,
                depth=depth,
                height=height
            )
            
        except ValidationError as e:
            raise ValidationError(f"Row {row_num}: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Row {row_num}: Unexpected error - {str(e)}")
    
    def export_arrangement_csv(self, items: Dict[str, Item]) -> str:
        """Export current arrangement to CSV format"""
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write header
        csv_writer.writerow(['Item ID', 'Container ID', 'Coordinates (W1,D1,H1)', 'Coordinates (W2,D2,H2)'])
        
        # Write item data
        for item in items.values():
            if item.containerId and item.position:
                start_coords = item.position['startCoordinates']
                end_coords = item.position['endCoordinates']
                
                start_str = f"({start_coords['width']},{start_coords['depth']},{start_coords['height']})"
                end_str = f"({end_coords['width']},{end_coords['depth']},{end_coords['height']})"
                
                csv_writer.writerow([
                    item.itemId,
                    item.containerId,
                    start_str,
                    end_str
                ])
        
        return csv_output.getvalue()
    
    def validate_csv_format(self, csv_content: str, expected_type: str) -> Tuple[bool, str]:
        """Validate CSV format before processing"""
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            headers = csv_reader.fieldnames
            
            if not headers:
                return False, "No headers found in CSV"
            
            if expected_type == "items":
                required_fields = self.required_item_fields
            elif expected_type == "containers":
                required_fields = self.required_container_fields
            else:
                return False, "Unknown CSV type"
            
            # Check for required headers
            missing_headers = [field for field in required_fields if field not in headers]
            if missing_headers:
                return False, f"Missing required headers: {', '.join(missing_headers)}"
            
            # Check if CSV has any data rows
            try:
                first_row = next(csv_reader)
                if not first_row:
                    return False, "CSV file appears to be empty"
            except StopIteration:
                return False, "CSV file has no data rows"
            
            return True, "CSV format is valid"
            
        except Exception as e:
            return False, f"CSV validation error: {str(e)}"
    
    def get_csv_sample(self, csv_type: str, num_rows: int = 5) -> str:
        """Generate sample CSV format for reference"""
        if csv_type == "items":
            headers = self.required_item_fields
            sample_data = [
                ["000001", "Food_Packet", "10.0", "10.0", "20.0", "5.0", "80", "2025-05-20", "30", "Crew_Quarters"],
                ["000002", "Oxygen_Cylinder", "15.0", "15.0", "50.0", "30.0", "95", "N/A", "100", "Airlock"],
                ["000003", "First_Aid_Kit", "20.0", "20.0", "10.0", "2.0", "100", "2025-07-10", "5", "Medical_Bay"]
            ]
        elif csv_type == "containers":
            headers = self.required_container_fields
            sample_data = [
                ["CQ01", "Crew_Quarters", "100.0", "85.0", "200.0"],
                ["A01", "Airlock", "50.0", "85.0", "200.0"],
                ["MB01", "Medical_Bay", "200.0", "85.0", "200.0"]
            ]
        else:
            return "Unknown CSV type"
        
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write header
        csv_writer.writerow(headers)
        
        # Write sample data
        for i, row in enumerate(sample_data):
            if i < num_rows:
                csv_writer.writerow(row)
        
        return csv_output.getvalue()

# Global CSV handler instance
csv_handler = CSVHandler()
