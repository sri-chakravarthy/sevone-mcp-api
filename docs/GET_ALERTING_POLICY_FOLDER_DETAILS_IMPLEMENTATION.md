# Get Alerting Policy Folder Details - Implementation Summary

## Overview

Successfully implemented the `get_alerting_policy_folder_details` tool for the SevOne MCP server. This tool retrieves all alerting policy folders from SevOne via the `GET /api/v3/policies/folders` endpoint.

## Implementation Details

### 1. Tool Implementation
**File**: `src/tools/get_alerting_policy_folder_details.py`

- **Class**: `GetAlertingPolicyFolderDetailsTool`
- **Method**: GET
- **Endpoint**: `/api/v3/policies/folders`
- **Parameters**: 
  - `page_size` (optional, default: 100, max: 1000)

**Response Format**:
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
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 alerting policy folders"
}
```

### 2. Server Registration
**File**: `src/server.py`

- Added import for `GetAlertingPolicyFolderDetailsTool`
- Instantiated tool in `__init__` method
- Registered tool in `list_tools` method
- Added tool routing in `call_tool` method

### 3. Documentation
**File**: `docs/GET_ALERTING_POLICY_FOLDER_DETAILS_TOOL.md`

Comprehensive documentation including:
- API endpoint details
- Tool parameters
- Response format
- Folder properties
- Usage examples
- Use cases
- Related tools
- Error handling

### 4. Mode Integration
**File**: `.bob/custom_modes.yaml`

Updated the `sevone-get-details` mode to include:
- Tool description in role definition
- When to use guidance
- Tool parameters and usage
- Query pattern examples
- Folder information structure

**Key Updates**:
- Added policy folder queries to mode description
- Included `get_alerting_policy_folder_details` in tool list
- Added example queries for folder operations
- Updated information includes section

### 5. Testing
**File**: `tests/test_get_alerting_policy_folder_details.py`

Comprehensive test suite with 9 tests covering:
- ✅ Tool properties validation
- ✅ Successful folder retrieval
- ✅ Custom page size handling
- ✅ Invalid page size validation (too small)
- ✅ Invalid page size validation (too large)
- ✅ Empty folders response
- ✅ API error handling
- ✅ Unexpected response format handling
- ✅ All folder fields populated

**Test Results**: All 9 tests passing ✅

## API Specification

Based on `api-docs/sevone-swagger.json`:

**Endpoint**: `GET /api/v3/policies/folders`

**Query Parameters**:
- `pagination.limit` (string, uint64)
- `pagination.offset` (string, uint64)
- `pagination.peerLimit` (string, uint64)
- `sorts.field` (enum: ID, NAME, PARENT_ID)
- `sorts.direction` (enum: DIRECTION_ASCENDING, DIRECTION_DESCENDING)

**Response Schema**: `sevone.api.v3.GetPolicyFoldersResponse`
```json
{
  "policyFolders": [
    {
      "id": "string (uint64)",
      "name": "string",
      "parentId": "string (uint64)",
      "isEditable": "boolean"
    }
  ]
}
```

## Usage Examples

### Example 1: Get All Folders
```python
# Using MCP tool
use_mcp_tool(
  server_name="sevone-api",
  tool_name="get_alerting_policy_folder_details",
  arguments={}
)
```

### Example 2: Get Folders with Custom Page Size
```python
use_mcp_tool(
  server_name="sevone-api",
  tool_name="get_alerting_policy_folder_details",
  arguments={
    "page_size": 50
  }
)
```

### Example 3: Use in Get Details Mode
User query: "List all policy folders"
- Mode: sevone-get-details
- Tool: get_alerting_policy_folder_details
- Result: All folders with IDs, names, parent relationships

## Integration with Existing Tools

The new tool complements existing alerting policy functionality:

1. **get_alerting_policy_folder_details** → Get folder IDs
2. **get_alerting_policy_details** → Filter policies by folder_ids

Example workflow:
```
1. Get all folders → folder_ids: [1, 2, 3]
2. Get policies in folder 2 → get_alerting_policy_details(folder_ids=[2])
```

## Key Features

✅ Simple, no-filter design - returns all folders
✅ Pagination support (1-1000 items)
✅ Hierarchical structure via parent_id
✅ Editable flag for system vs user folders
✅ Comprehensive error handling
✅ Full test coverage
✅ Clear documentation
✅ Integrated with sevone-get-details mode

## Files Modified/Created

### Created:
1. `src/tools/get_alerting_policy_folder_details.py` - Tool implementation
2. `docs/GET_ALERTING_POLICY_FOLDER_DETAILS_TOOL.md` - Documentation
3. `tests/test_get_alerting_policy_folder_details.py` - Test suite
4. `docs/GET_ALERTING_POLICY_FOLDER_DETAILS_IMPLEMENTATION.md` - This file

### Modified:
1. `src/server.py` - Tool registration
2. `.bob/custom_modes.yaml` - Mode integration

## Verification

All implementation requirements met:
- ✅ Tool calls GET /api/v3/policies/folders
- ✅ Returns folder IDs in JSON format
- ✅ Based on Swagger documentation
- ✅ Registered in MCP server
- ✅ Integrated with sevone-get-details mode
- ✅ Mode prompts kept crisp
- ✅ Comprehensive testing
- ✅ Full documentation

## Next Steps

The tool is ready for use. To test with live SevOne API:
1. Ensure MCP server is running
2. Use sevone-get-details mode
3. Query: "List all policy folders"
4. Verify folder structure and IDs

## Made with Bob