# Get Device Metadata IDs Tool

## Overview

The `get_device_metadata_ids` tool retrieves device metadata namespace and attribute IDs from SevOne NMS. This tool provides a convenient interface to query metadata information by device IDs or by namespace and attribute name combinations.

## API Endpoint

- **Endpoint**: `POST /api/v3/metadata/devices/metadata`
- **Method**: POST
- **Authentication**: Required (handled automatically by the MCP server)

## Tool Name

```
get_device_metadata_ids
```

## Input Parameters

The tool accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `device_ids` | array of integers | Conditional* | List of device IDs (entityIds) to query metadata for |
| `namespace` | string | Conditional* | Metadata namespace name to filter by |
| `attribute_name` | string | Conditional* | Metadata attribute name to filter by (requires namespace) |
| `page_size` | integer | No | Number of results per page (default: 100, max: 1000) |

\* **Note**: Either `device_ids` OR both `namespace` and `attribute_name` must be provided.

## Response Format

The tool returns a JSON object with the following structure:

```json
{
  "success": true,
  "data": {
    "devices": {
      "device_id": {
        "device_id": "123",
        "device_name": "router1",
        "namespaces": {
          "namespace_name": {
            "namespace_id": "1",
            "namespace_name": "System",
            "attributes": {
              "attribute_name": {
                "attribute_id": "10",
                "attribute_name": "Location",
                "attribute_type": "STRING",
                "values": {
                  "value_id": "value"
                },
                "entity_types": ["DEVICE"],
                "singleton": true,
                "validation_expression": ""
              }
            }
          }
        }
      }
    },
    "total_devices": 1,
    "raw_response": {}
  },
  "message": "Successfully retrieved metadata for 1 device(s)"
}
```

## Usage Examples

### Example 1: Get Metadata for Specific Devices

Query metadata for devices with IDs 123 and 456:

```json
{
  "device_ids": [123, 456]
}
```

### Example 2: Get Specific Attribute by Namespace and Name

Query for a specific metadata attribute across all devices:

```json
{
  "namespace": "System",
  "attribute_name": "Location"
}
```

### Example 3: Get Metadata for Devices with Specific Attribute

Query metadata for specific devices filtered by namespace and attribute:

```json
{
  "device_ids": [123, 456],
  "namespace": "Custom",
  "attribute_name": "Site"
}
```

### Example 4: Query with Custom Page Size

Query with a larger page size:

```json
{
  "device_ids": [123, 456, 789],
  "page_size": 500
}
```

## Response Fields

### Device Metadata Structure

Each device in the response contains:

- **device_id**: The device ID
- **device_name**: The device name
- **namespaces**: Dictionary of namespace objects

### Namespace Structure

Each namespace contains:

- **namespace_id**: The unique ID of the namespace
- **namespace_name**: The name of the namespace
- **attributes**: Dictionary of attribute objects

### Attribute Structure

Each attribute contains:

- **attribute_id**: The unique ID of the attribute
- **attribute_name**: The name of the attribute
- **attribute_type**: The data type (STRING, DATETIME, INTEGER, IP, etc.)
- **values**: Dictionary of attribute values (key-value pairs)
- **entity_types**: Array of entity types this attribute applies to (e.g., ["DEVICE"])
- **singleton**: Boolean indicating if only one value is allowed
- **validation_expression**: Regular expression for value validation (if any)

## Error Handling

The tool returns error information in the following format:

```json
{
  "success": false,
  "error": "Error message details",
  "message": "Failed to get device metadata IDs"
}
```

Common errors:

1. **Missing Parameters**: Either `device_ids` or both `namespace` and `attribute_name` must be provided
2. **Invalid Parameter Combination**: `attribute_name` requires `namespace` to be specified
3. **API Errors**: Network issues, authentication failures, or invalid device IDs

## Use Cases

1. **Metadata Discovery**: Find all metadata namespaces and attributes for specific devices
2. **Attribute ID Lookup**: Get the namespace ID and attribute ID for a specific metadata field
3. **Metadata Validation**: Retrieve validation rules and data types for metadata attributes
4. **Bulk Metadata Query**: Query metadata for multiple devices in a single request
5. **Metadata Structure Analysis**: Understand the metadata schema and available attributes

## Notes

- The tool automatically handles authentication using the configured SevOne credentials
- Results include both processed data (for easy consumption) and raw API response
- The `page_size` parameter controls pagination but defaults to 100 results
- Namespace and attribute names are case-sensitive
- The tool returns all namespaces and attributes for the queried devices unless filtered

## Related Tools

- [`get_device_details`](GET_DEVICE_DETAILS_TOOL.md): Get comprehensive device information
- [`get_device_group_details`](GET_DEVICE_GROUP_DETAILS_TOOL.md): Get device group information
- [`run_api_endpoint`](../README.md#run_api_endpoint-tool): Execute any SevOne API endpoint

## API Documentation Reference

For more details about the underlying API endpoint, refer to:
- SevOne REST API Documentation: `/api/v3/metadata/devices/metadata`
- Swagger Definition: `api-docs/sevone-swagger.json` (lines 11876-12000, 35996-36073)

---

*Made with Bob*