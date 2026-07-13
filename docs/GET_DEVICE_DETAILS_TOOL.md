# get_device_details Tool Documentation

## Overview

The `get_device_details` tool provides a convenient interface to query device information from SevOne NMS. It wraps the `/api/v3/devices/list` endpoint and supports multiple query methods.

## Tool Information

- **Name**: `get_device_details`
- **Endpoint**: `POST /api/v3/devices/list`
- **Authentication**: Automatic (handled by token manager)

## Features

- Query devices by names, IDs, or device group IDs
- Support for fuzzy matching with wildcards
- Optional metadata inclusion
- Pagination support
- Comprehensive device information in response

## Input Parameters

### Required (at least one of):

- **device_names** (array of strings): List of device names to query
  - Supports exact or fuzzy matching
  - Example: `["router1", "switch2"]`
  
- **device_ids** (array of integers): List of device IDs to query
  - Example: `[123, 456, 789]`
  
- **device_group_ids** (array of integers): List of device group IDs to query
  - Example: `[10, 20]`

### Optional:

- **fuzzy_match** (boolean): Enable fuzzy matching for device names
  - Default: `false`
  - When `true`, supports wildcards like `"router*"`, `"*switch*"`
  - Example: `true`

- **include_metadata** (boolean): Include device metadata in response
  - Default: `false`
  - When `true`, returns metadata attributes for each device
  - Example: `true`

- **page_size** (integer): Number of devices to return per page
  - Default: `100`
  - Minimum: `1`
  - Maximum: `1000`
  - Example: `50`

## Response Format

```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "id": "123",
        "name": "router1",
        "displayName": "Router 1",
        "ip": "192.168.1.1",
        "description": "Main router",
        "deviceClass": "Router",
        "timezone": "America/New_York",
        "alertCount": 2,
        "maxSeverity": "MAJOR",
        "plugins": [...],
        "metadata": {...}  // Only if include_metadata=true
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 device(s)"
}
```

## Usage Examples

### Example 1: Get Devices by Names

```json
{
  "device_names": ["router1", "switch2", "firewall1"]
}
```

### Example 2: Get Devices by IDs

```json
{
  "device_ids": [123, 456, 789]
}
```

### Example 3: Get Devices by Group IDs

```json
{
  "device_group_ids": [10, 20]
}
```

### Example 4: Fuzzy Search with Wildcards

```json
{
  "device_names": ["router*", "*switch*"],
  "fuzzy_match": true,
  "page_size": 50
}
```

### Example 5: Get Devices with Metadata

```json
{
  "device_names": ["router1"],
  "include_metadata": true
}
```

### Example 6: Combined Query

```json
{
  "device_ids": [123, 456],
  "device_group_ids": [10],
  "include_metadata": true,
  "page_size": 100
}
```

## Device Information Returned

Each device object in the response includes:

- **id**: Unique device identifier
- **name**: Device name
- **displayName**: Display name for the device
- **ip**: IP address
- **description**: Device description
- **deviceClass**: Device class/type
- **timezone**: Device timezone
- **alertCount**: Number of active alerts
- **maxSeverity**: Highest alert severity
- **discoveryStatus**: Discovery status
- **plugins**: Array of plugin information
- **deviceGroupMembership**: Device group memberships
- **metadata**: Device metadata (if requested)

## Error Handling

The tool returns structured error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "message": "Failed to get device details"
}
```

Common errors:
- Missing required parameters (no device_names, device_ids, or device_group_ids)
- Invalid device IDs or names
- Network/API errors
- Authentication failures

## Best Practices

1. **Use Specific Queries**: Query by device IDs when possible for better performance
2. **Limit Page Size**: Use appropriate page_size to avoid large responses
3. **Fuzzy Matching**: Use fuzzy_match=true only when needed for wildcard searches
4. **Metadata**: Only request metadata when necessary to reduce response size
5. **Error Handling**: Always check the `success` field in the response

## Comparison with run_api_endpoint

While you can use `run_api_endpoint` to call `/api/v3/devices/list` directly, `get_device_details` provides:

- Simplified parameter interface
- Automatic request body construction
- Built-in validation
- Better error messages
- Type-safe parameters

### Using run_api_endpoint (more complex):

```json
{
  "endpoint": "/api/v3/devices/list",
  "method": "POST",
  "data": {
    "request": {
      "deviceNames": [
        {"value": "router1", "isFuzzy": false}
      ],
      "pagination": {"size": 100}
    }
  }
}
```

### Using get_device_details (simpler):

```json
{
  "device_names": ["router1"],
  "page_size": 100
}
```

## Integration Examples

### Python (using MCP client):

```python
result = await mcp_client.call_tool(
    "get_device_details",
    {
        "device_names": ["router1"],
        "include_metadata": True
    }
)

if result["success"]:
    devices = result["data"]["devices"]
    for device in devices:
        print(f"Device: {device['name']} - IP: {device['ip']}")
```

### Bob AI Usage:

```
Get details for devices named router1 and switch2
```

Bob will automatically use the `get_device_details` tool with appropriate parameters.

## Related Tools

- **run_api_endpoint**: Generic API endpoint execution
- Future tools: `create_device`, `update_device`, `delete_device`

## API Reference

For complete API documentation, see:
- SevOne API Swagger: `api-docs/sevone-swagger.json`
- Endpoint: `/api/v3/devices/list`
- Request schema: `sevone.api.v3.ListDevicesRequest`
- Response schema: `sevone.api.v3.ListDevicesResponse`

---

**Last Updated**: 2026-05-19  
**Version**: 1.0.0  
**Author**: Bob AI Assistant