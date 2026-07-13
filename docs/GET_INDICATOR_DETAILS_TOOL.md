# Get Indicator Details Tool

## Overview

The `get_indicator_details` tool retrieves comprehensive indicator information from SevOne NMS. It provides flexible querying capabilities using 15 different filter options, making it easy to find specific indicators across your monitoring infrastructure.

## API Endpoint

- **Method**: POST
- **Endpoint**: `/api/v3/metadata/indicators`
- **Authentication**: Required (handled automatically)

## Features

- **15 Filter Options**: Query indicators using device IDs, names, objects, types, metadata, and more
- **Fuzzy Matching**: Support for wildcard searches (e.g., `router*`)
- **Large Response Handling**: Automatic truncation and clear messaging for large result sets
- **Memory-Efficient**: Built-in response size validation and compression support
- **Pagination**: Configurable page size (1-1000 indicators per request)

## Input Parameters

### Device Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_ids` | array[integer] | List of device IDs to query indicators for |
| `device_names` | array[string] | List of device names (supports fuzzy matching) |

### Device-Object Combinations

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_object_pairs` | array[array[string]] | List of [deviceName, objectName] pairs. Each pair must have exactly 2 strings. |

### Indicator Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `indicator_ids` | array[integer] | List of specific indicator IDs |
| `indicator_type_ids` | array[integer] | List of indicator type IDs |
| `indicator_type_descriptions` | array[string] | List of indicator type descriptions |
| `indicator_type_names` | array[string] | List of indicator type names |

### Object Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `object_ids` | array[integer] | List of object IDs |
| `object_type_ids` | array[integer] | List of object type IDs |
| `object_type_paths` | array[array[string]] | List of object type paths (hierarchical) |

### Plugin Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `plugin_ids` | array[integer] | List of plugin IDs |

### Triple Combinations

| Parameter | Type | Description |
|-----------|------|-------------|
| `device_object_indicator_triples` | array[array[integer]] | List of [deviceId, objectId, indicatorId] triples. Each triple must have exactly 3 integers. |

### Metadata Filters

#### Device Metadata
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `device_metadata_namespace` | string | Yes* | Device metadata namespace |
| `device_metadata_attribute` | string | Yes* | Device metadata attribute name |
| `device_metadata_value` | string | Yes* | Device metadata attribute value |

*All three parameters must be provided together

#### Object Group
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_group_class_name` | string | Yes* | Object group class name |
| `object_group_name` | string | Yes* | Object group name |

*Both parameters must be provided together

#### Object Metadata
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `object_metadata_namespace` | string | Yes* | Object metadata namespace |
| `object_metadata_attribute` | string | Yes* | Object metadata attribute name |
| `object_metadata_value` | string | Yes* | Object metadata attribute value |

*All three parameters must be provided together

### Additional Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fuzzy_match` | boolean | false | Enable fuzzy matching for names (supports wildcards like `router*`) |
| `page_size` | integer | 100 | Number of indicators per page (min: 1, max: 1000) |

## Response Format

```json
{
  "success": true,
  "data": {
    "indicators": [
      {
        "id": "789",
        "indicatorTypeId": "5",
        "indicatorTypeName": "CPU Usage",
        "indicatorTypeDescription": "Percentage of CPU utilization",
        "deviceId": "123",
        "deviceName": "router1",
        "objectId": "456",
        "objectName": "eth0",
        "pluginId": "1",
        "enabled": true
      }
    ],
    "total_count": 1,
    "truncated": false
  },
  "message": "Successfully retrieved 1 indicator(s)"
}
```

### Truncated Response

When more than 100 indicators are returned, the response is automatically truncated:

```json
{
  "success": true,
  "data": {
    "indicators": [...],  // First 100 indicators
    "total_count": 250,
    "truncated": true,
    "truncated_message": "Showing 100 of 250 indicators. Use pagination or add more filters to see specific results."
  },
  "message": "Successfully retrieved 250 indicator(s)"
}
```

## Usage Examples

### Example 1: Get Indicators by Device IDs

```json
{
  "device_ids": [123, 456, 789]
}
```

### Example 2: Get Indicators by Device Names (Fuzzy Match)

```json
{
  "device_names": ["router*", "switch*"],
  "fuzzy_match": true
}
```

### Example 3: Get Indicators by Device-Object Pairs

```json
{
  "device_object_pairs": [
    ["router1", "eth0"],
    ["router1", "eth1"],
    ["switch2", "port1"]
  ]
}
```

### Example 4: Get Indicators by Type Names

```json
{
  "indicator_type_names": ["CPU Usage", "Memory Usage", "Bandwidth"],
  "page_size": 50
}
```

### Example 5: Get Indicators by Device Metadata

```json
{
  "device_metadata_namespace": "System",
  "device_metadata_attribute": "Location",
  "device_metadata_value": "Building A"
}
```

### Example 6: Get Indicators by Object Group

```json
{
  "object_group_class_name": "Interface",
  "object_group_name": "WAN Interfaces"
}
```

### Example 7: Get Specific Indicators by Triple

```json
{
  "device_object_indicator_triples": [
    [123, 456, 789],
    [123, 457, 790]
  ]
}
```

### Example 8: Combine Multiple Filters

```json
{
  "device_ids": [123],
  "indicator_type_names": ["CPU Usage"],
  "object_ids": [456, 457],
  "page_size": 200
}
```

## Error Handling

### Missing Required Parameters

```json
{
  "success": false,
  "error": "At least one filter must be provided",
  "message": "Missing required parameters"
}
```

### Incomplete Metadata Parameters

```json
{
  "success": false,
  "error": "All three device metadata parameters (namespace, attribute, value) must be provided together",
  "message": "Invalid device metadata parameters"
}
```

### API Errors

```json
{
  "success": false,
  "error": "Response too large (75.50MB exceeds limit of 50MB). Consider reducing page_size or adding more filters.",
  "message": "Failed to get indicator details"
}
```

## Best Practices

### 1. Use Specific Filters
Start with the most specific filter available to reduce response size:
- Use `indicator_ids` when you know the exact indicators
- Use `device_ids` instead of `device_names` when possible
- Combine multiple filters to narrow results

### 2. Manage Large Result Sets
- Use `page_size` parameter to control response size
- Start with smaller page sizes (50-100) for exploratory queries
- Add more specific filters if you receive truncated results

### 3. Fuzzy Matching
- Use fuzzy matching sparingly as it can return large result sets
- Combine fuzzy matching with other filters to narrow results
- Use specific wildcards (e.g., `router-core*` instead of `router*`)

### 4. Metadata Queries
- Ensure all three metadata parameters are provided together
- Use exact values for metadata attributes when possible
- Consider querying metadata IDs first using `get_device_metadata_ids` tool

### 5. Performance Optimization
- Query during off-peak hours for large result sets
- Use pagination for iterative data retrieval
- Cache results when querying the same indicators repeatedly

## Response Size Management

The tool implements several safeguards for large responses:

1. **Size Validation**: Responses exceeding 50MB are rejected with a clear error message
2. **Automatic Truncation**: Results over 100 indicators are truncated with a warning
3. **Compression**: Automatic gzip/deflate compression for bandwidth efficiency
4. **Memory Protection**: JSON parsing errors and memory issues are caught and reported

## Related Tools

- **get_device_details**: Query device information before retrieving indicators
- **get_object_details**: Query object information to find relevant objects
- **get_device_metadata_ids**: Discover available metadata namespaces and attributes
- **run_api_endpoint**: Direct API access for advanced queries

## Troubleshooting

### Issue: "Response too large" Error

**Solution**: 
- Reduce `page_size` parameter
- Add more specific filters (device IDs, indicator type IDs)
- Query in smaller batches

### Issue: No Results Returned

**Solution**:
- Verify filter values are correct
- Try fuzzy matching if using exact names
- Check if indicators exist for the specified devices/objects
- Verify metadata namespace and attribute names

### Issue: Truncated Results

**Solution**:
- This is expected for large result sets (>100 indicators)
- Add more specific filters to narrow results
- Use pagination to retrieve specific subsets
- Consider querying by device or object groups

## Implementation Notes

- Built on SevOne REST API v3
- Supports all 15 filter types from the Swagger specification
- Implements automatic response truncation for user experience
- Includes comprehensive error handling and validation
- Thread-safe and async-compatible

## Version History

- **v1.0.0** (2026-06-03): Initial implementation with all 15 filter options

---

**Made with Bob**