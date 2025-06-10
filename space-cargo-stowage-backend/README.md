# Space Cargo Stowage Backend API Documentation

<!-- 
DOCUMENTATION NOTES:
- Response structures in this documentation are based on frontend API usage patterns and may need verification against actual backend implementation
- Some coordinate systems and data formats are assumed based on common 3D placement patterns
- Error response formats are standardized assumptions and should be confirmed with actual backend error handling
- CSV formats are based on existing test files but header variations may exist
- Query parameter names and optional/required status inferred from frontend code patterns
-->

## Important Assumptions & Constraints

⚠️ **Data Model Assumptions:**
- All IDs (itemId, containerId, userId) are assumed to be unique strings
- Physical dimensions (width, depth, height) are in consistent units across items and containers
- Weight values are in consistent mass units (assumed kilograms)
- Zone identifiers must match between items and containers for proper placement
- Expiry dates are stored as ISO 8601 UTC timestamps
- Container dimensions represent internal usable space, not external dimensions

⚠️ **Business Logic Assumptions:**
- Items can only be placed in containers with matching or compatible zones
- Physical constraints assume items fit entirely within container dimensions
- Usage limits represent consumable item depletion (0 = fully depleted)
- Waste items are considered items that have reached expiry or usage limits
- Simulation represents daily time progression in space environment

⚠️ **CSV Format Assumptions:**
- Headers may contain spaces (automatically trimmed during processing)
- Data values may contain leading/trailing spaces (automatically cleaned)
- Date formats in CSV should be parseable by JavaScript Date constructor
- Required fields must be present and non-empty after cleaning

⚠️ **API Response Assumptions:**
- All responses include HTTP status codes for proper error handling
- Error messages are human-readable and suitable for frontend display
- Success responses include relevant data objects or confirmation messages
- Array responses may be empty but will always be valid arrays

## Overview
This backend provides a comprehensive API for managing space cargo operations, including item placement, container management, waste handling, simulation, and system logging. The API is built with Express.js and uses PostgreSQL for data persistence.

## Server Configuration
- **Base URL**: `http://localhost:8000`
- **Default Port**: 8000 (configurable via `PORT` environment variable)
- **CORS**: Enabled for all origins
- **Content-Type**: Supports `application/json` and `multipart/form-data`

## API Endpoints

### 🔧 Item Management

#### `POST /api/placement`
**Purpose**: Automatically optimize and place items in containers using algorithmic placement

⚠️ **Placement Algorithm Assumptions:**
- Uses 3D bin packing algorithms for optimal space utilization
- Assumes items are rectangular/cuboid shaped for placement calculations  
- Zone matching is strict - items only placed in containers with matching zones
- Weight distribution and center of gravity calculations are not implemented
- Items cannot be rotated during placement (fixed orientation)
- Algorithm prioritizes volume efficiency over accessibility

- **Request Body**:
  ```json
  {
    "items": [
      {
        "itemId": "string",
        "name": "string",
        "width": "number",
        "depth": "number", 
        "height": "number",
        "weight": "number",
        "preferredZone": "string"
      }
    ],
    "containers": [
      {
        "containerId": "string",
        "zone": "string",
        "width": "number",
        "depth": "number",
        "height": "number"
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "placements": [
      {
        "itemId": "string",
        "containerId": "string",
        "coordinates": {
          "x1": "number",
          "y1": "number", 
          "z1": "number",
          "x2": "number",
          "y2": "number",
          "z2": "number"
        }
      }
    ],
    "unplacedItems": [
      {
        "itemId": "string",
        "reason": "string"
      }
    ],
    "totalItemsPlaced": "number",
    "totalUnplacedItems": "number"
  }
  ```
- **Features**: 
  - Saves items and containers to database
  - Uses optimization algorithms for efficient placement
  - Updates item-container assignments

#### `GET /api/search`
**Purpose**: Search for specific items and get retrieval steps
- **Query Parameters**:
  - `itemId` (string): Specific item identifier
  - `itemName` (string): Item name for fuzzy search
  - `userId` (string, optional): User performing the search
- **Response**:
  ```json
  {
    "success": true,
    "found": true,
    "item": [
      {
        "itemId": "string",
        "name": "string",
        "containerId": "string",
        "coordinates": {
          "x": "number",
          "y": "number",
          "z": "number"
        }
      }
    ],
    "retrievalSteps": [
      {
        "step": "number",
        "action": "remove|setAside|retrieve|placeBack",
        "itemId": "string",
        "itemName": "string"
      }
    ]
  }
  ```
- **Features**:
  - Returns detailed retrieval steps for item access
  - Handles item not found scenarios

#### `POST /api/retrieve`
**Purpose**: Log item retrieval and decrement usage limits
- **Request Body**:
  ```json
  {
    "itemId": "string",
    "userId": "string",
    "timestamp": "ISO string"
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```
- **Features**: Updates item usage counters and logs retrieval activity

#### `POST /api/place`
**Purpose**: Manually place an item in a specific container location
- **Request Body**:
  ```json
  {
    "itemId": "string",
    "userId": "string",
    "timestamp": "ISO string",
    "containerId": "string",
    "position": {
      "startCoordinates": {"x": "number", "y": "number", "z": "number"},
      "endCoordinates": {"x": "number", "y": "number", "z": "number"}
    }
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Item placed successfully",
    "placement": {
      "itemId": "string",
      "containerId": "string",
      "coordinates": {
        "x1": "number",
        "y1": "number",
        "z1": "number",
        "x2": "number",
        "y2": "number",
        "z2": "number"
      }
    }
  }
  ```
- **Features**: Allows precise manual positioning with coordinate validation

#### `GET /api/item/get-some`
**Purpose**: Retrieve items with flexible filtering options
- **Query Parameters**:
  - `itemNumbers` (integer): Limit number of items returned
  - `itemName` (string): Filter by item name
  - `itemId` (string): Filter by specific item ID
- **Response**:
  ```json
  {
    "success": true,
    "items": [
      {
        "itemId": "string",
        "name": "string",
        "width": "number",
        "depth": "number",
        "height": "number",
        "weight": "number",
        "usageLimit": "number",
        "expiryDate": "ISO string",
        "preferredZone": "string",
        "containerId": "string"
      }
    ],
    "count": "number"
  }
  ```
- **Features**: Supports pagination and multiple search criteria

### 📦 Container Management

#### `GET /api/container/get-all`
**Purpose**: Retrieve all available containers
- **Parameters**: None
- **Response**:
  ```json
  {
    "containers": [
      {
        "containerId": "string",
        "zone": "string",
        "width": "number",
        "depth": "number",
        "height": "number"
      }
    ]
  }
  ```
- **Features**: 
  - Returns standardized container data format
  - Includes dimensional specifications for placement calculations

### ♻️ Waste Management

#### `GET /api/waste/identify`
**Purpose**: Automatically identify items that should be returned to Earth
- **Parameters**: None
- **Response**:
  ```json
  {
    "success": true,
    "wasteItems": [
      {
        "itemId": "string",
        "name": "string",
        "containerId": "string",
        "reason": "expired|depleted|damaged",
        "dateIdentified": "ISO string",
        "volume": "number",
        "weight": "number"
      }
    ]
  }
  ```
- **Features**: 
  - Analyzes item usage patterns and expiration
  - Generates waste recommendations

#### `POST /api/waste/return-plan`
**Purpose**: Create an optimal waste return plan for undocking
- **Request Body**:
  ```json
  {
    "undockingContainerId": "string",
    "undockingDate": "ISO string",
    "maxVolume": "number"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "returnPlan": [
      {
        "step": "number",
        "itemId": "string",
        "itemName": "string",
        "fromContainer": "string",
        "toContainer": "string"
      }
    ],
    "retrievalSteps": [
      {
        "step": "number",
        "action": "remove|setAside|retrieve|placeBack",
        "itemId": "string",
        "itemName": "string"
      }
    ],
    "returnManifest": {
      "undockingContainerId": "string",
      "undockingDate": "ISO string",
      "returnItems": [
        {
          "itemId": "string",
          "name": "string",
          "reason": "string"
        }
      ],
      "totalVolume": "number"
    }
  }
  ```
- **Features**:
  - Optimizes volume utilization for return container
  - Generates step-by-step retrieval plan
  - Creates return manifest for documentation

#### `POST /api/waste/complete-undocking`
**Purpose**: Finalize waste container undocking and remove items from inventory
- **Request Body**:
  ```json
  {
    "undockingContainerId": "string",
    "timestamp": "ISO string"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "itemsRemoved": "number"
  }
  ```
- **Features**: Permanently removes waste items from active inventory

### 🎮 Simulation

#### `POST /api/simulate/day`
**Purpose**: Simulate time progression and item usage over multiple days

⚠️ **Simulation Logic Assumptions:**
- Each item usage decrements usageLimit by 1 (linear consumption model)
- Items are considered expired if current simulation date > expiryDate
- Items are depleted when usageLimit reaches 0
- Daily usage applies to specified items only - other items remain unchanged
- Time progression is simplified - does not account for real-world usage patterns
- No random events or equipment failures are simulated

- **Request Body**:
  ```json
  {
    "numOfDays": "integer",
    "toTimestamp": "ISO string",
    "itemsToBeUsedPerDay": [
      {
        "itemId": "string",
        "name": "string"
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "newDate": "ISO string",
    "changes": {
      "itemsUsed": [
        {
          "itemId": "string",
          "name": "string",
          "remainingUses": "number"
        }
      ],
      "itemsExpired": [
        {
          "itemId": "string",
          "name": "string"
        }
      ],
      "itemsDepletedToday": [
        {
          "itemId": "string",
          "name": "string"
        }
      ]
    }
  }
  ```
- **Features**:
  - Processes daily item consumption
  - Tracks expiration dates
  - Identifies depleted items
  - Supports both day count and target date simulation

### 📁 Import/Export Operations

#### `POST /api/import/items`
**Purpose**: Import items from CSV file upload

⚠️ **CSV Import Assumptions:**
- CSV file must use comma as delimiter (standard CSV format)
- Headers can have spaces but field names must match expected schema after trimming
- Empty rows are automatically skipped during processing
- Invalid data types (e.g., non-numeric dimensions) will cause row rejection
- Duplicate itemId values will be rejected to maintain uniqueness
- Date parsing uses JavaScript Date constructor - format should be ISO or common formats

- **Content-Type**: `multipart/form-data`
- **Form Data**: `csvFile` (file upload)
- **CSV Format**: `item_id, name, width, depth, height, weight, usage_limit, expiry_date, preferred_zone`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Items imported and placed successfully",
    "importResults": {
      "itemsImported": "number",
      "errors": ["string"],
      "totalProcessed": "number"
    },
    "optimizationResults": {
      "totalItemsPlaced": "number",
      "unplacedItems": "number"
    }
  }
  ```
- **Features**:
  - Validates CSV format and data integrity
  - Handles data cleaning (trimming spaces)
  - Automatic optimization placement after import

#### `POST /api/import/containers`
**Purpose**: Import containers from CSV file upload
- **Content-Type**: `multipart/form-data`
- **Form Data**: `csvFile` (file upload)
- **CSV Format**: `container_id, zone, width, depth, height`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Containers imported successfully",
    "importResults": {
      "containersImported": "number",
      "errors": ["string"],
      "totalProcessed": "number"
    }
  }
  ```
- **Features**:
  - Validates container specifications
  - Handles duplicate detection
  - Data cleaning and normalization

#### `GET /api/export/arrangements`
**Purpose**: Export current item placements to CSV file
- **Parameters**: None
- **Response**: CSV file download with headers:
  ```
  Content-Type: text/csv
  Content-Disposition: attachment; filename="cargo-arrangements-{timestamp}.csv"
  ```
  **CSV Content**:
  ```
  Item ID,Container ID,Coordinates (W1,D1,H1),(W2,D2,H2)
  ITM001,CNT001,"(0.0,0.0,0.0)","(10.5,8.2,5.0)"
  ```
- **Features**:
  - Generates timestamped file names
  - Includes precise coordinate information
  - Formatted for external analysis tools

### 📊 System Logging

#### `GET /api/logs`
**Purpose**: Retrieve filtered system logs for audit and analysis
- **Query Parameters**:
  - `startDate` (required): Start date in ISO format
  - `endDate` (required): End date in ISO format
  - `itemId` (optional): Filter by specific item
  - `userId` (optional): Filter by user activity
  - `actionType` (optional): Filter by action type (`placement`, `retrieval`, `rearrangement`, `disposal`)
- **Response**:
  ```json
  {
    "logs": [
      {
        "timestamp": "ISO string",
        "userId": "string",
        "actionType": "placement|retrieval|rearrangement|disposal",
        "itemId": "string",
        "details": {
          "fromContainer": "string",
          "toContainer": "string",
          "reason": "string"
        }
      }
    ]
  }
  ```
- **Features**:
  - Date range validation
  - Multiple filter combinations
  - Structured log format for analysis

#### `GET /api/logs/some-logs`
**Purpose**: Retrieve recent system logs with default limits
- **Query Parameters**:
  - `limit` (optional, default: 50): Number of recent logs to return
- **Response**:
  ```json
  {
    "logs": [
      {
        "timestamp": "ISO string",
        "userId": "string",
        "actionType": "placement|retrieval|rearrangement|disposal",
        "itemId": "string",
        "details": {
          "fromContainer": "string",
          "toContainer": "string",
          "reason": "string"
        }
      }
    ]
  }
  ```
- **Features**: Quick access to recent system activity

## Data Models

### Item Structure
```javascript
{
  itemId: "string",           // ASSUMPTION: Unique alphanumeric identifier (e.g., "ITM001", "FOOD_PACK_42")
  name: "string",             // ASSUMPTION: Human-readable item name (e.g., "Emergency Food Pack", "Water Filter")
  width: "number",            // ASSUMPTION: Physical dimension in centimeters or standard units
  depth: "number",            // ASSUMPTION: Physical dimension in centimeters or standard units
  height: "number",           // ASSUMPTION: Physical dimension in centimeters or standard units
  weight: "number",           // ASSUMPTION: Weight in kilograms or standard mass units
  usageLimit: "number",       // ASSUMPTION: Integer representing how many times item can be used before depletion
  expiryDate: "ISO string",   // ASSUMPTION: UTC timestamp (e.g., "2025-12-31T23:59:59Z") when item expires
  preferredZone: "string",    // ASSUMPTION: Zone identifier matching container zones (e.g., "A", "B", "MEDICAL", "FOOD")
  containerId: "string"       // ASSUMPTION: References Container.containerId where item is currently placed
}
```

### Container Structure
```javascript
{
  containerId: "string",      // ASSUMPTION: Unique alphanumeric identifier (e.g., "CNT001", "STORAGE_A_01")
  zone: "string",             // ASSUMPTION: Logical grouping identifier (e.g., "A", "B", "MEDICAL", "FOOD", "TOOLS")
  width: "number",            // ASSUMPTION: Internal usable dimension in same units as items
  depth: "number",            // ASSUMPTION: Internal usable dimension in same units as items
  height: "number"            // ASSUMPTION: Internal usable dimension in same units as items
}
```

### Log Entry Structure
```javascript
{
  timestamp: "ISO string",                        // ASSUMPTION: UTC timestamp when action occurred
  userId: "string",                               // ASSUMPTION: Unique identifier for crew member/user
  actionType: "placement|retrieval|rearrangement|disposal", // ASSUMPTION: Predefined action categories
  itemId: "string",                               // ASSUMPTION: References Item.itemId that was affected
  details: {
    fromContainer: "string",                      // ASSUMPTION: Source container ID (null for new placements)
    toContainer: "string",                        // ASSUMPTION: Destination container ID (null for removals)
    reason: "string"                              // ASSUMPTION: Human-readable explanation for the action
  }
}
```

## Error Handling

All endpoints return standardized error responses:

```javascript
{
  success: false,
  message: "Error description",
  error: "Technical error details" // when applicable
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## File Upload Configuration

- **Upload Directory**: `./uploads/`
- **Supported Formats**: CSV files only
- **File Naming**: Timestamped format (`{timestamp}-{originalname}`)
- **Automatic Cleanup**: Failed uploads are automatically removed

## Database Integration

The API integrates with PostgreSQL through dedicated models:
- `ItemsModel`: Item CRUD operations
- `ContainersModel`: Container management
- `WasteModel`: Waste identification and handling
- `SimulationModel`: Time progression and usage tracking
- `SystemlogsModel`: Audit logging
- `ImportExportModel`: CSV processing and validation

## Optimization Services

The backend includes sophisticated optimization algorithms:
- **Item Placement**: 3D bin packing algorithms
- **Waste Selection**: Volume and priority optimization
- **Retrieval Planning**: Minimal disturbance path calculation

## Getting Started

1. **Prerequisites**: Node.js, PostgreSQL
2. **Installation**: `npm install`
3. **Environment**: Configure `.env` with database credentials
4. **Database**: Run `initDatabase()` to set up schema
5. **Start Server**: `npm start` or `nodemon server.js`

The server will initialize the database connection and start listening on the configured port.

## Implementation Notes & Known Limitations

### Data Consistency
- **Coordinate System**: All coordinates are assumed to be in a 3D Cartesian system with origin at container bottom-left-front
- **Unit Consistency**: No automatic unit conversion - all dimensions must use the same unit system
- **Zone Validation**: Zone matching is case-sensitive and requires exact string matches

### Performance Considerations
- **Placement Algorithm**: O(n²) complexity for item-container matching - may be slow with large datasets
- **CSV Processing**: Large CSV files (>1000 items) may cause timeout on placement optimization
- **Database Queries**: No pagination implemented for large result sets

### Security Limitations
- **File Upload**: Limited CSV validation - malicious files could cause processing errors
- **Input Sanitization**: Basic validation only - no SQL injection protection beyond parameterized queries
- **Authentication**: No user authentication or authorization implemented

### Space Environment Specifics
- **Microgravity**: Physics calculations do not account for microgravity effects on item placement
- **Structural Integrity**: No analysis of vibration, acceleration, or structural stress during transport
- **Emergency Access**: Retrieval algorithms do not prioritize emergency/critical items

### Data Model Limitations
- **Item Shapes**: Only rectangular/cuboid items supported - no irregular shapes
- **Container Types**: All containers treated as simple rectangular storage - no specialized equipment
- **Usage Patterns**: Linear usage consumption model may not reflect real-world usage patterns
- **Environmental Factors**: No temperature, pressure, or contamination considerations

### Integration Assumptions
- **Database Schema**: Assumes specific PostgreSQL table structure - schema changes require code updates
- **Frontend API**: Response formats are tailored to current frontend implementation
- **External Systems**: No integration with real space mission systems or NASA databases

### Development Status
- **Error Handling**: Basic error responses - may need enhancement for production use
- **Logging**: System logs are comprehensive but may need log rotation for long-term use
- **Testing**: API functions are validated through frontend integration but lack comprehensive unit tests
- **Documentation**: Response structures are based on frontend usage patterns and may need verification

⚠️ **Production Readiness**: This API is designed for educational/demonstration purposes and would require significant enhancements for actual space mission deployment, including robust error handling, security features, comprehensive testing, and integration with mission-critical systems.
