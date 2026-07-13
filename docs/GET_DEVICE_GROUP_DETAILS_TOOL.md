# get_device_group_details Tool Documentation

## Overview

The `get_device_group_details` tool provides a convenient interface for querying device group information from SevOne NMS. It wraps the `/api/v3/devicegroups/list` API endpoint and supports querying by device group IDs or hierarchical device group paths.

## Tool Information

- **Name**: `get_device_group_details`
- **API Endpoint**: `POST /api/v3/devicegroups/list`
- **Authentication**: Automatic (handled by TokenManager)

## Input Parameters

The tool accepts the following parameters (at least one is required):

### device_group_ids (optional)
- **Type**: Array of integers
- **Description**: List of device group IDs to query
- **Example**: `[1, 2, 3]`

### device_group_paths (optional)
- **Type**: Array of strings
- **Description**: List of hierarchical device group paths. Each path string is treated as a single path component (the '/' characters are part of the path name, not separators).
- **Example**: `["All Device Groups/AP/IND", "All Device Groups/EU"]`
- **Note**: The entire path string (including any '/' characters) is sent as a single path component to the API.

### include_metadata (optional)
- **Type**: Boolean
- **Default**: `false`
- **Description**: Whether to include device group metadata in the response

### page_size (optional)
- **Type**: Integer
- **Default**: `100`
- **Range**: 1-1000
- **Description**: Number of device groups to return per page

## Response Format

The tool returns a JSON object with the following structure:

```json
{
  "status": "success",
  "device_groups": [
    {
      "id": "123",
      "name": "IND",
      "description": "India device group",
      "path": {
        "pathComponents": ["All Device Groups", "AP", "IND"]
      },
      "metadata": {}  // Only if include_metadata=true
    }
  ],
  "total_count": 1,
  "message": "Successfully retrieved 1 device groups"
}
```

### Error Response

```json
{
  "status": "error",
  "error": "Error message here",
  "device_groups": [],
  "total_count": 0,
  "message": "An error occurred while retrieving device group details"
}
```

## Usage Examples

### Example 1: Query by Device Group IDs

```python
from tools.get_device_group_details import GetDeviceGroupDetailsTool

tool = GetDeviceGroupDetailsTool()
result = await tool.execute(
    api_client,
    device_group_ids=[1, 2, 3]
)
```

### Example 2: Query by Device Group Paths

```python
result = await tool.execute(
    api_client,
    device_group_paths=[
        "All Device Groups/AP/IND",
        "All Device Groups/EU/UK"
    ]
)
```

### Example 3: Query with Metadata

```python
result = await tool.execute(
    api_client,
    device_group_paths=["All Device Groups/AP"],
    include_metadata=True
)
```

### Example 4: Query with Custom Page Size

```python
result = await tool.execute(
    api_client,
    device_group_ids=[1, 2, 3, 4, 5],
    page_size=50
)
```

## MCP Tool Usage

When using this tool through the MCP protocol:

```json
{
  "name": "get_device_group_details",
  "arguments": {
    "device_group_paths": [
      "All Device Groups/AP/IND"
    ],
    "include_metadata": true
  }
}
```

## API Request Details

The tool constructs a request to the SevOne API with the following structure:

```json
{
  "ids": ["1", "2"],
  "paths": [
    {
      "pathComponents": ["All Device Groups/AP/IND"]
    }
  ],
  "metadataAttributes": [],
  "pagination": {
    "size": 100
  }
}
```

## Notes

1. **At least one filter required**: You must provide either `device_group_ids` or `device_group_paths`
2. **Path format**: Device group paths are strings that may contain '/' characters. The entire path string is treated as a single path component and sent to the API as-is (e.g., `"All Device Groups/AP/IND"` becomes `{"pathComponents": ["All Device Groups/AP/IND"]}`).
3. **ID format**: Device group IDs are converted to strings in the API request
4. **Pagination**: Results are paginated with a default page size of 100
5. **Metadata**: Metadata is only included if explicitly requested via `include_metadata=True`

## Error Handling

The tool handles the following error scenarios:

- **Missing required parameters**: Returns error if neither device_group_ids nor device_group_paths is provided
- **API errors**: Catches and returns API errors with descriptive messages
- **Network errors**: Handles connection issues and timeouts
- **Authentication errors**: Automatic token refresh on 401 responses

## Related Tools

- [`get_device_details`](GET_DEVICE_DETAILS_TOOL.md) - Query device information
- [`run_api_endpoint`](../README.md#run_api_endpoint-tool) - Generic API endpoint execution

## Implementation Details

- **File**: `src/tools/get_device_group_details.py`
- **Class**: `GetDeviceGroupDetailsTool`
- **Async**: Yes (uses async/await)
- **Dependencies**: 
  - `SevOneAPIClient` for API calls
  - `TokenManager` for authentication (automatic)

## Testing

Test the tool using:

```bash
python tests/test_get_device_group_details.py
```

Or test directly:

```python
import asyncio
from tools.get_device_group_details import GetDeviceGroupDetailsTool

async def test():
    # Initialize API client (see main README)
    result = await tool.execute(
        api_client,
        device_group_ids=[1]
    )
    print(result)

asyncio.run(test())