from fastapi import APIRouter, HTTPException, UploadFile, File, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List, Dict
from backend.models.log_entry import LogEntry
from backend.storage.csv_handler import csv_handler
from backend.storage.memory_store import storage
import time

router = APIRouter()

# Response models
class ImportResponse(BaseModel):
    success: bool
    itemsImported: int = 0
    containersImported: int = 0
    errors: List[Dict] = []

@router.post("/import/items", response_model=ImportResponse)
async def import_items(file: UploadFile = File(...)):
    """
    Import items from CSV file
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate CSV format
        is_valid, validation_message = csv_handler.validate_csv_format(csv_content, "items")
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {validation_message}")
        
        # Parse CSV
        items, errors = csv_handler.parse_items_csv(csv_content)
        
        # Import items to storage
        items_imported = 0
        if items:
            items_imported = storage.add_multiple_items(items)
        
        # Log import
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="import",
            itemId=None,
            details={
                "import_type": "items",
                "filename": file.filename,
                "total_items_in_file": len(items) + len(errors),
                "items_imported": items_imported,
                "errors_count": len(errors)
            }
        )
        storage.add_log(log_entry)
        
        return ImportResponse(
            success=True,
            itemsImported=items_imported,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="import",
            itemId=None,
            details={
                "import_type": "items",
                "filename": file.filename if file else "unknown",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.post("/import/containers", response_model=ImportResponse)
async def import_containers(file: UploadFile = File(...)):
    """
    Import containers from CSV file
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate CSV format
        is_valid, validation_message = csv_handler.validate_csv_format(csv_content, "containers")
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {validation_message}")
        
        # Parse CSV
        containers, errors = csv_handler.parse_containers_csv(csv_content)
        
        # Import containers to storage
        containers_imported = 0
        if containers:
            containers_imported = storage.add_multiple_containers(containers)
        
        # Log import
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="import",
            itemId=None,
            details={
                "import_type": "containers",
                "filename": file.filename,
                "total_containers_in_file": len(containers) + len(errors),
                "containers_imported": containers_imported,
                "errors_count": len(errors)
            }
        )
        storage.add_log(log_entry)
        
        return ImportResponse(
            success=True,
            containersImported=containers_imported,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="import",
            itemId=None,
            details={
                "import_type": "containers",
                "filename": file.filename if file else "unknown",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")

@router.get("/export/arrangement")
async def export_arrangement():
    """
    Export current item arrangement as CSV
    """
    try:
        # Get all items
        items = storage.get_all_items()
        
        # Generate CSV
        csv_content = csv_handler.export_arrangement_csv(items)
        
        # Log export
        placed_items = sum(1 for item in items.values() if item.containerId and item.position)
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "arrangement",
                "total_items": len(items),
                "placed_items": placed_items
            }
        )
        storage.add_log(log_entry)
        
        # Return CSV file
        filename = f"arrangement_export_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        return PlainTextResponse(
            content=csv_content,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv"
            }
        )
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "arrangement",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/items")
async def export_items():
    """
    Export all items as CSV
    """
    try:
        # Get all items
        items = storage.get_all_items()
        
        # Generate CSV content manually for items
        import io
        import csv
        
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write header
        csv_writer.writerow([
            'item_id', 'name', 'width_cm', 'depth_cm', 'height_cm', 
            'mass_kg', 'priority', 'expiry_date', 'usage_limit', 
            'preferred_zone', 'current_uses', 'container_id', 'placement_timestamp'
        ])
        
        # Write item data
        for item in items.values():
            csv_writer.writerow([
                item.itemId,
                item.name,
                item.width,
                item.depth,
                item.height,
                item.mass,
                item.priority,
                item.expiryDate or 'N/A',
                item.usageLimit,
                item.preferredZone,
                item.currentUses,
                item.containerId or '',
                item.placementTimestamp or ''
            ])
        
        csv_content = csv_output.getvalue()
        
        # Log export
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "items",
                "total_items": len(items)
            }
        )
        storage.add_log(log_entry)
        
        # Return CSV file
        filename = f"items_export_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        return PlainTextResponse(
            content=csv_content,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv"
            }
        )
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "items",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/export/containers")
async def export_containers():
    """
    Export all containers as CSV
    """
    try:
        # Get all containers
        containers = storage.get_all_containers()
        
        # Generate CSV content manually for containers
        import io
        import csv
        
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        
        # Write header
        csv_writer.writerow(['container_id', 'zone', 'width_cm', 'depth_cm', 'height_cm'])
        
        # Write container data
        for container in containers.values():
            csv_writer.writerow([
                container.containerId,
                container.zone,
                container.width,
                container.depth,
                container.height
            ])
        
        csv_content = csv_output.getvalue()
        
        # Log export
        log_entry = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "containers",
                "total_containers": len(containers)
            }
        )
        storage.add_log(log_entry)
        
        # Return CSV file
        filename = f"containers_export_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        return PlainTextResponse(
            content=csv_content,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/csv"
            }
        )
        
    except Exception as e:
        # Log error
        error_log = LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            userId="system",
            actionType="export",
            itemId=None,
            details={
                "export_type": "containers",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        storage.add_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"Export error: {str(e)}")

@router.get("/samples/items")
async def get_sample_items_csv():
    """
    Get sample CSV format for items
    """
    try:
        sample_csv = csv_handler.get_csv_sample("items", num_rows=5)
        
        return PlainTextResponse(
            content=sample_csv,
            headers={
                "Content-Disposition": "attachment; filename=sample_items.csv",
                "Content-Type": "text/csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample generation error: {str(e)}")

@router.get("/samples/containers")
async def get_sample_containers_csv():
    """
    Get sample CSV format for containers
    """
    try:
        sample_csv = csv_handler.get_csv_sample("containers", num_rows=5)
        
        return PlainTextResponse(
            content=sample_csv,
            headers={
                "Content-Disposition": "attachment; filename=sample_containers.csv",
                "Content-Type": "text/csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample generation error: {str(e)}")

@router.get("/import/status")
async def get_import_status():
    """
    Get current import status and data overview
    """
    try:
        # Get storage statistics
        stats = storage.get_statistics()
        
        return {
            "success": True,
            "status": stats,
            "import_guidelines": {
                "items_csv_format": "item_id,name,width_cm,depth_cm,height_cm,mass_kg,priority,expiry_date,usage_limit,preferred_zone",
                "containers_csv_format": "container_id,zone,width_cm,depth_cm,height_cm",
                "notes": [
                    "All CSV files must have headers in the first row",
                    "Item IDs will be zero-padded to 6 digits",
                    "Priority should be 1-100 (higher = more important)",
                    "Expiry dates should be ISO format or 'N/A'",
                    "All dimensions are in centimeters",
                    "Mass is in kilograms"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status error: {str(e)}")

@router.post("/import/validate")
async def validate_csv_file(file: UploadFile = File(...), file_type: str = "items"):
    """
    Validate CSV file format without importing
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate CSV format
        is_valid, validation_message = csv_handler.validate_csv_format(csv_content, file_type)
        
        if is_valid:
            # Parse to check for data errors without importing
            if file_type == "items":
                items, errors = csv_handler.parse_items_csv(csv_content)
                return {
                    "success": True,
                    "valid": True,
                    "message": "CSV format is valid",
                    "totalRows": len(items) + len(errors),
                    "validRows": len(items),
                    "errorRows": len(errors),
                    "errors": errors[:10]  # Show first 10 errors
                }
            else:
                containers, errors = csv_handler.parse_containers_csv(csv_content)
                return {
                    "success": True,
                    "valid": True,
                    "message": "CSV format is valid",
                    "totalRows": len(containers) + len(errors),
                    "validRows": len(containers),
                    "errorRows": len(errors),
                    "errors": errors[:10]  # Show first 10 errors
                }
        else:
            return {
                "success": True,
                "valid": False,
                "message": validation_message,
                "errors": []
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")
