# Get Alerting Policy Folder Details Tool

## Overview

The `get_alerting_policy_folder_details` tool retrieves all alerting policy folders from SevOne. This tool provides information about the folder structure used to organize alerting policies.

## API Endpoint

- **Endpoint**: `GET /api/v3/policies/folders`
- **Method**: GET
- **Authentication**: Required (Bearer token)

## Tool Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page_size` | integer | No | 100 | Number of folders to return per page (min: 1, max: 1000) |

## Response Format

```json
{
  "success": true,
  "data": {
    "folders": [
      {
        "id": "1",
        "name": "Default Policies",
        "parent_id": "0",
        "is_editable": true
      },
      {
        "id": "2",
        "name": "Network Policies",
        "parent_id": "1",
        "is_editable": true
      }
    ],
    "total_count": 2
  },
  "message": "Successfully retrieved 2 alerting policy folders"
}
```

## Folder Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier for the folder |
| `name` | string | Name of the folder |
| `parent_id` | string | ID of the parent folder (0 for root folders) |
| `is_editable` | boolean | Whether the folder can be edited |

## Usage Examples

### Example 1: Get All Folders

```json
{}
```

This retrieves all policy folders with default pagination (100 folders).

### Example 2: Get Folders with Custom Page Size

```json
{
  "page_size": 50
}
```

This retrieves up to 50 policy folders.

## Use Cases

1. **Folder Discovery**: List all available policy folders in the system
2. **Folder Hierarchy**: Understand the parent-child relationships between folders
3. **Policy Organization**: Identify where policies are organized
4. **Integration**: Use folder IDs to filter policies in `get_alerting_policy_details`

## Related Tools

- **get_alerting_policy_details**: Use folder IDs from this tool to filter policies by folder
- **create_device_group**: Similar hierarchical structure for device groups

## Error Handling

The tool returns structured error responses:

```json
{
  "success": false,
  "error": "page_size must be between 1 and 1000",
  "message": "Invalid parameters"
}
```

## Notes

- Folders are returned in a flat list; parent-child relationships are indicated by `parent_id`
- Root folders have `parent_id` of "0"
- The `is_editable` flag indicates whether the folder is a system folder or user-created
- Pagination is supported but all folders are typically returned in a single request

## Implementation Details

- **File**: `src/tools/get_alerting_policy_folder_details.py`
- **Class**: `GetAlertingPolicyFolderDetailsTool`
- **API Version**: v3

## Made with Bob