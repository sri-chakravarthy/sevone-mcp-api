# get_object_details Tool Documentation

## Overview

The `get_object_details` tool provides a convenient interface to query object information from SevOne NMS. It wraps the `/api/v3/objects/list` endpoint and supports multiple query methods.

## Tool Information

- **Name**: `get_object_details`
- **Endpoint**: `POST /api/v3/objects/list`
- **Authentication**: Automatic (handled by token manager)

## Features

- Query objects by device ID, device name, or device group paths
- Filter by device metadata (namespace, attribute, value)
- Filter by device and object name combination
- Filter by object group (class name and group name)
- Filter by object metadata (namespace, attribute, value)
- Support for fuzzy matching with wildcards
- Optional metadata inclusion
- Pagination support
- Comprehensive object information in response

## Input Parameters

### Required (at least one of):

#### Device Filters:

- **device_id** (integer): Device ID to query objects for
  - Example: `123`
  
- **device_name** (string): Device name to query objects for
  - Supports exact or fuzzy matching
  - Example: `"router1"`
  
- **device_group_paths** (array of arrays): List of device group paths (hierarchical paths)
  - Each path is an array of strings representing the path components
  - Example: `[["All Device Groups", "West", "Seattle"]]`

#### Device Metadata Filter:

- **device_metadata_namespace** (string): Device metadata namespace
  - Must be used with `device_metadata_attribute` and `device_metadata_value`
  - Example: `"System"`
  
- **device_metadata_attribute** (string): Device metadata attribute name
  - Must be used with `device_metadata_namespace` and `device_metadata_value`
  - Example: `"Location"`
  
- **device_metadata_value** (string): Device metadata attribute value
  - Must be used with `device_metadata_namespace` and `device_metadata_attribute`
  - Example: `"Building A"`

#### Object Group Filter:

- **object_group_class_name** (string): Object group class name
  - Must be used with `object_group_name`
  - Example: `"Interface"`
  
- **object_group_name** (string): Object group name
  - Must be used with `object_group_class_name`
  - Example: `"WAN Interfaces"`

#### Object Metadata Filter:

- **object_metadata_namespace** (string): Object metadata namespace
  - Must be used with `object_metadata_attribute` and `object_metadata_value`
  - Example: `"Custom"`
  
- **object_metadata_attribute** (string): Object metadata attribute name
  - Must be used with `object_metadata_namespace` and `object_metadata_value`
  - Example: `"Type"`
  
- **object_metadata_value** (string): Object metadata attribute value
  - Must be used with `object_metadata_namespace` and `object_metadata_attribute`
  - Example: `"Critical"`

### Optional:

- **object_name** (string): Object name to filter by
  - Used in combination with `device_name`
  - Supports exact or fuzzy matching
  - Example: `"eth0"`

- **fuzzy_match** (boolean): Enable fuzzy matching for device and object names
  - Default: `false`
  - When `true`, supports wildcards like `"router*"`, `"*eth*"`
  - Example: `true`

- **include_metadata** (boolean): Include object metadata in response
  - Default: `false`
  - When `true`, returns metadata attributes for each object
  - Example: `true`

- **page_size** (integer): Number of objects to return per page
  - Default: `100`
  - Minimum: `1`
  - Maximum: `1000`
  - Example: `50`

## Response Format

```json
{
  "success": true,
  "data": {
    "objects": [
      {
        "id": "456",
        "name": "eth0",
        "displayName": "Ethernet 0",
        "deviceId": "123",
        "deviceName": "router1",
        "pluginId": "1",
        "pluginName": "SNMP",
        "objectType": "Interface",
        "objectClass": "Network Interface",
        "metadata": {...}  // Only if include_metadata=true
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 object(s)"
}
```

## Usage Examples

### Example 1: Get Objects by Device ID

```json
{
  "device_id": 123
}
```

### Example 2: Get Objects by Device Name

```json
{
  "device_name": "router1"
}
```

### Example 3: Get Specific Object by Device and Object Name

```json
{
  "device_name": "router1",
  "object_name": "eth0"
}
```

### Example 4: Get Objects by Device Group Path

```json
{
  "device_group_paths": [
    ["All Device Groups", "West", "Seattle"]
  ]
}
```

### Example 5: Get Objects by Device Metadata

```json
{
  "device_metadata_namespace": "System",
  "device_metadata_attribute": "Location",
  "device_metadata_value": "Building A"
}
```

### Example 6: Get Objects by Object Group

```json
{
  "object_group_class_name": "Interface",
  "object_group_name": "WAN Interfaces"
}
```

### Example 7: Get Objects by Object Metadata

```json
{
  "object_metadata_namespace": "Custom",
  "object_metadata_attribute": "Type",
  "object_metadata_value": "Critical"
}
```

### Example 8: Fuzzy Search with Wildcards

```json
{
  "device_name": "router*",
  "object_name": "eth*",
  "fuzzy_match": true,
  "page_size": 50
}
```

### Example 9: Get Objects with Metadata

```json
{
  "device_id": 123,
  "include_metadata": true
}
```

### Example 10: Combined Query

```json
{
  "device_name": "router1",
  "object_name": "eth0",
  "include_metadata": true,
  "page_size": 100
}
```

## Object Information Returned

Each object in the response includes:

- **id**: Unique object identifier
- **name**: Object name
- **displayName**: Display name for the object
- **deviceId**: ID of the device this object belongs to
- **deviceName**: Name of the device
- **pluginId**: Plugin identifier
- **pluginName**: Name of the plugin
- **objectType**: Type of the object
- **objectClass**: Class of the object
- **metadata**: Object metadata (if requested)

## Error Handling

The tool returns structured error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "message": "Failed to get object details"
}
```

Common errors:
- Missing required parameters (no valid filter provided)
- Incomplete metadata parameters (missing namespace, attribute, or value)
- Incomplete object group parameters (missing class name or group name)
- Invalid device IDs or names
- Network/API errors
- Authentication failures

## Best Practices

1. **Use Specific Queries**: Query by device ID when possible for better performance
2. **Limit Page Size**: Use appropriate page_size to avoid large responses
3. **Fuzzy Matching**: Use fuzzy_match=true only when needed for wildcard searches
4. **Metadata**: Only request metadata when necessary to reduce response size
5. **Error Handling**: Always check the `success` field in the response
6. **Combine Filters**: Use device_name with object_name for precise queries
7. **Metadata Filters**: Ensure all three metadata parameters are provided together

## Query Patterns

### By Device

```
User: "Get objects for device 123"
→ Tool: get_object_details, device_id=123

User: "Show objects for router1"
→ Tool: get_object_details, device_name="router1"
```

### By Device and Object

```
User: "Find eth0 on router1"
→ Tool: get_object_details, device_name="router1", object_name="eth0"

User: "Show all eth interfaces on router*"
→ Tool: get_object_details, device_name="router*", object_name="eth*", fuzzy_match=true
```

### By Device Group

```
User: "List objects in Seattle office"
→ Tool: get_object_details, device_group_paths=[["All Device Groups", "West", "Seattle"]]
```

### By Device Metadata

```
User: "Get objects for devices in Building A"
→ Tool: get_object_details, device_metadata_namespace="System", 
    device_metadata_attribute="Location", device_metadata_value="Building A"
```

### By Object Group

```
User: "Show WAN interfaces"
→ Tool: get_object_details, object_group_class_name="Interface", 
    object_group_name="WAN Interfaces"
```

### By Object Metadata

```
User: "Find critical objects"
→ Tool: get_object_details, object_metadata_namespace="Custom", 
    object_metadata_attribute="Type", object_metadata_value="Critical"
```

## Comparison with run_api_endpoint

While you can use `run_api_endpoint` to call `/api/v3/objects/list` directly, `get_object_details` provides:

- Simplified parameter interface
- Automatic request body construction
- Built-in validation
- Better error messages
- Type-safe parameters
- Support for multiple query methods

### Using run_api_endpoint (more complex):

```json
{
  "endpoint": "/api/v3/objects/list",
  "method": "POST",
  "data": {
    "devices": [
      {"device": "123"}
    ],
    "pagination": {"size": 100}
  }
}
```

### Using get_object_details (simpler):

```json
{
  "device_id": 123,
  "page_size": 100
}
```

## Integration Examples

### Python (using MCP client):

```python
result = await mcp_client.call_tool(
    "get_object_details",
    {
        "device_name": "router1",
        "object_name": "eth0",
        "include_metadata": True
    }
)

if result["success"]:
    objects = result["data"]["objects"]
    for obj in objects:
        print(f"Object: {obj['name']} - Device: {obj['deviceName']}")
```

### Bob AI Usage:

```
Get objects for device router1
```

Bob will automatically use the `get_object_details` tool with appropriate parameters.

## Related Tools

- **get_device_details**: Query device information
- **get_device_group_details**: Query device group information
- **get_device_metadata_ids**: Get metadata namespace and attribute IDs
- **run_api_endpoint**: Generic API endpoint execution

## API Reference

For complete API documentation, see:
- SevOne API Swagger: `api-docs/sevone-swagger.json`
- Endpoint: `/api/v3/objects/list`
- Request schema: `sevone.api.v3.ListObjectsRequest`
- Response schema: `sevone.api.v3.ListObjectsResponse`

## Filter Combinations

The tool supports various filter combinations:

| Filter Type | Required Parameters | Optional Parameters |
|-------------|---------------------|---------------------|
| Device ID | device_id | object_name, fuzzy_match, include_metadata |
| Device Name | device_name | object_name, fuzzy_match, include_metadata |
| Device Group | device_group_paths | include_metadata |
| Device Metadata | device_metadata_namespace, device_metadata_attribute, device_metadata_value | include_metadata |
| Object Group | object_group_class_name, object_group_name | include_metadata |
| Object Metadata | object_metadata_namespace, object_metadata_attribute, object_metadata_value | include_metadata |

**Note**: At least ONE filter type must be provided. Multiple filters can be combined (e.g., device_name + object_name).

## Troubleshooting

### No objects found?
- Verify the device exists and has objects
- Try using fuzzy matching with wildcards
- Check if the object name is spelled correctly
- Ensure the device group path is correct

### Need more information?
- Add `include_metadata=true` to your query
- Query by device ID for faster results
- Use specific object names when known

### Query too slow?
- Reduce the page_size parameter
- Be more specific with device names or IDs
- Use device ID instead of device name when possible

### Metadata filter not working?
- Ensure all three metadata parameters are provided (namespace, attribute, value)
- Verify the metadata namespace and attribute names are correct
- Check that the metadata value matches exactly (or use fuzzy matching)

---

**Last Updated**: 2026-06-01  
**Version**: 1.0.0  
**Author**: Bob AI Assistant