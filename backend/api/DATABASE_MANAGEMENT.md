# Database Management API Documentation

## Overview
The Database Management API provides endpoints for managing the in-memory database state. These endpoints are crucial for testing, evaluation, and development workflows.

## Endpoints

### 1. Clear Database
**Endpoint:** `POST /api/database/clear`  
**Purpose:** Clear all data from the database  
**Use Cases:** 
- Before running evaluations
- Testing with fresh data
- Resetting system state

**Request:** No body required

**Response:**
```json
{
  "success": true,
  "message": "Database cleared successfully",
  "details": {
    "items_cleared": true,
    "containers_cleared": true,
    "logs_cleared": true,
    "simulation_reset": true,
    "processing_time_ms": 5.2
  }
}
```

### 2. Database Status
**Endpoint:** `GET /api/database/status`  
**Purpose:** Get current database statistics  
**Use Cases:**
- Checking current data state
- Monitoring system usage
- Debugging data issues

**Request:** No parameters required

**Response:**
```json
{
  "success": true,
  "database_status": {
    "items": {
      "total": 150,
      "placed": 140,
      "unplaced": 10
    },
    "containers": {
      "total": 25,
      "details": [
        {
          "containerId": "EA01",
          "zone": "Medical_Bay",
          "itemCount": 5,
          "dimensions": "100x100x100"
        }
      ]
    },
    "logs": {
      "total": 200
    },
    "simulation": {
      "current_date": "2025-06-16T20:30:45.123456"
    }
  }
}
```

### 3. Reset Database
**Endpoint:** `POST /api/database/reset`  
**Purpose:** Reset database to initial clean state  
**Use Cases:**
- Complete system reset
- Preparation for new test scenarios
- Recovery from corrupted state

**Request:** No body required

**Response:**
```json
{
  "success": true,
  "message": "Database reset to initial state",
  "details": {
    "all_data_cleared": true,
    "simulation_reset_to_now": true,
    "processing_time_ms": 3.1
  }
}
```

## Frontend Integration

### Recommended UI Elements

1. **Clear Database Button**
   - Red button with warning confirmation
   - Text: "Clear All Data"
   - Confirmation dialog: "Are you sure? This will remove all items, containers, and logs."

2. **Database Status Display**
   - Dashboard widget showing current counts
   - Real-time updates
   - Color-coded status indicators

3. **Reset System Button**
   - Orange button with double confirmation
   - Text: "Reset System"
   - Confirmation: "This will completely reset the system. Continue?"

### Example Frontend Code

```javascript
// Clear Database
async function clearDatabase() {
  if (confirm("Are you sure you want to clear all data?")) {
    const response = await fetch('/api/database/clear', {
      method: 'POST'
    });
    const result = await response.json();
    if (result.success) {
      alert('Database cleared successfully');
      refreshDashboard();
    }
  }
}

// Get Status
async function getDatabaseStatus() {
  const response = await fetch('/api/database/status');
  const result = await response.json();
  return result.database_status;
}
```

## Testing Workflow

1. **Before Evaluation:**
   ```bash
   curl -X POST http://localhost:8000/api/database/clear
   ```

2. **Check Status:**
   ```bash
   curl -X GET http://localhost:8000/api/database/status
   ```

3. **Reset for New Test:**
   ```bash
   curl -X POST http://localhost:8000/api/database/reset
   ```

## Security Notes

- These endpoints can completely wipe data
- Consider adding authentication in production
- Add rate limiting for reset endpoints
- Log all database management operations

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `500` - Internal server error

Error response format:
```json
{
  "detail": "Database clear error: specific error message"
}
```
