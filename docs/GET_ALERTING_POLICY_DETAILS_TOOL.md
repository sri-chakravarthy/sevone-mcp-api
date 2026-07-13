# Get Alerting Policy Details Tool

## Overview

The `get_alerting_policy_details` tool allows you to query alerting policies in SevOne by various criteria including name, alert severities, policy IDs, device group ID, and enabled/disabled status.

## Tool Name

`get_alerting_policy_details`

## Description

This tool retrieves detailed information about alerting policies by querying with one or more of:
- Policy name (supports fuzzy matching)
- List of alert severities (subset of EMERGENCY, CRITICAL, ERROR, WARNING)
- List of policy IDs
- List of folder IDs
- Device group ID
- Enabled/Disabled status

The tool returns comprehensive policy information including policy ID, name, description, alert severity, enabled/disabled status, device group association, policy type, trigger/clear expressions, and last updated timestamp.

## API Endpoint

- **Method**: POST
- **Endpoint**: `/api/v3/policies/filter`

## Parameters

### Optional Parameters (at least one must be provided)

- `name` (string): Policy name to search for (supports fuzzy matching)
- `alert_severities` (array of strings): List of alert severities to filter by
  - Valid values: `["EMERGENCY", "CRITICAL", "ERROR", "WARNING"]`
  - Can be a subset of these values
- `policy_ids` (array of integers): List of policy IDs to query
- `folder_ids` (array of integers): List of folder IDs to filter policies by
- `device_group_id` (integer): Device group ID to filter policies by
- `is_enabled` (boolean): Filter by enabled (`true`) or disabled (`false`) status
- `page_size` (integer): Number of policies to return per page (default: 100, max: 1000)

**Note**: Multiple filters can be combined. Policies must match ALL specified criteria.

## Response Format

```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "id": 123,
        "name": "High CPU Alert",
        "description": "Alert when CPU exceeds threshold",
        "severity": "CRITICAL",
        "is_enabled": true,
        "is_device_group": false,
        "policy_type": "POLICY_TYPE_OTHER",
        "trigger_expression": "value > 90",
        "clear_expression": "value < 80",
        "last_updated": "2024-01-01T00:00:00Z",
        "folder_id": 1,
        "object_type_id": 10,
        "object_sub_type_id": 20
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 alerting policies"
}
```

## Usage Examples

### Example 1: Get Policy by Name

Query for a policy by its name (with fuzzy matching):

```json
{
  "name": "High CPU Alert"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "id": 123,
        "name": "High CPU Alert",
        "severity": "CRITICAL",
        "is_enabled": true
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 alerting policies"
}
```

### Example 2: Get Policies by Alert Severities

Query for all CRITICAL and ERROR policies:

```json
{
  "alert_severities": ["CRITICAL", "ERROR"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "id": 456,
        "name": "Critical Alert",
        "severity": "CRITICAL",
        "is_enabled": true
      },
      {
        "id": 789,
        "name": "Error Alert",
        "severity": "ERROR",
        "is_enabled": true
      }
    ],
    "total_count": 2
  },
  "message": "Successfully retrieved 2 alerting policies"
}
```

### Example 3: Get Policies by IDs

Query for specific policies by their IDs:

```json
{
  "policy_ids": [123, 456, 789]
}
```

### Example 4: Get Policies by Folder IDs

Query for policies in specific folders:

```json
{
  "folder_ids": [1, 2]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "id": 555,
        "name": "Folder Policy 1",
        "severity": "WARNING",
        "is_enabled": true,
        "folder_id": 1
      },
      {
        "id": 666,
        "name": "Folder Policy 2",
        "severity": "ERROR",
        "is_enabled": true,
        "folder_id": 2
      }
    ],
    "total_count": 2
  },
  "message": "Successfully retrieved 2 alerting policies"
}
```

### Example 5: Get Policies for Device Group

Query for all policies associated with a specific device group:

```json
{
  "device_group_id": 10
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "policies": [
      {
        "id": 789,
        "name": "Group Policy",
        "severity": "ERROR",
        "is_enabled": true,
        "is_device_group": true,
        "device_group_id": 10
      }
    ],
    "total_count": 1
  },
  "message": "Successfully retrieved 1 alerting policies"
}
```

### Example 6: Get Enabled Policies

Query for all enabled policies:

```json
{
  "is_enabled": true
}
```

### Example 7: Get Disabled Policies

Query for all disabled policies:

```json
{
  "is_enabled": false
}
```

### Example 8: Combined Filters

Query for enabled CRITICAL policies in a specific device group and folder:

```json
{
  "alert_severities": ["CRITICAL"],
  "is_enabled": true,
  "device_group_id": 10,
  "folder_ids": [1]
}
```

### Example 9: Custom Page Size

Query with a custom page size:

```json
{
  "name": "Alert",
  "page_size": 50
}
```

## Policy Information Fields

The tool returns the following information for each policy:

- `id`: Policy ID (integer)
- `name`: Policy name (string)
- `description`: Policy description (string)
- `severity`: Alert severity level (string)
  - Possible values: EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG, NONE
- `is_enabled`: Whether the policy is enabled (boolean)
- `is_device_group`: Whether this is a device group policy (boolean)
- `device_group_id`: Device group ID (integer, only present if `is_device_group` is true)
- `policy_type`: Type of policy (string)
  - Possible values: POLICY_TYPE_UNKNOWN, POLICY_TYPE_OTHER, POLICY_TYPE_FLOW
- `trigger_expression`: Expression that triggers the alert (string)
- `clear_expression`: Expression that clears the alert (string)
- `last_updated`: Timestamp of last update (string, ISO 8601 format)
- `folder_id`: Folder ID where policy is stored (integer)
- `object_type_id`: Object type ID (integer)
- `object_sub_type_id`: Object sub-type ID (integer)

## Error Handling

The tool returns detailed error information if the operation fails:

```json
{
  "success": false,
  "error": "At least one filter criterion must be provided",
  "message": "Missing required parameters"
}
```

Common errors:
- No filter criteria provided
- Invalid alert severity values (must be subset of EMERGENCY, CRITICAL, ERROR, WARNING)
- Invalid page_size (must be between 1 and 1000)
- API connection errors

## Notes

1. **Filter Criteria**: At least one filter criterion must be provided (name, alert_severities, policy_ids, folder_ids, device_group_id, or is_enabled).

2. **Multiple Filters**: When multiple filters are specified, policies must match ALL criteria (AND logic).

3. **Fuzzy Matching**: The `name` parameter supports fuzzy matching, allowing partial name searches.

4. **Alert Severities**: Only a subset of severities can be queried: EMERGENCY, CRITICAL, ERROR, WARNING. Other severity levels (ALERT, NOTICE, INFO, DEBUG, NONE) are not supported in the filter.

5. **Folder Organization**: Policies are organized in folders. Use `folder_ids` to filter policies by their folder location.

6. **Device Group Policies**: Policies can be associated with device groups. When `is_device_group` is true, the `device_group_id` field will be present in the response.

7. **Pagination**: The tool supports pagination through the `page_size` parameter. Default is 100, maximum is 1000.

8. **Policy Types**: Policies can be of different types (OTHER or FLOW). The type affects how the policy is evaluated.

## Workflow Tips

### Finding Policies by Name

If you know part of the policy name:

```json
{
  "name": "CPU"
}
```

This will return all policies with "CPU" in their name due to fuzzy matching.

### Finding Critical Issues

To find all critical and emergency policies:

```json
{
  "alert_severities": ["EMERGENCY", "CRITICAL"]
}
```

### Auditing Disabled Policies

To find all disabled policies for review:

```json
{
  "is_enabled": false
}
```

### Folder-based Policy Management

To find all policies in specific folders:

```json
{
  "folder_ids": [1, 2, 3]
}
```

### Device Group Policy Management

To find all policies for a specific device group:

```json
{
  "device_group_id": 10,
  "is_enabled": true
}
```

### Combined Folder and Device Group Filtering

To find enabled policies in specific folders for a device group:

```json
{
  "folder_ids": [1],
  "device_group_id": 10,
  "is_enabled": true
}
```

## Related Tools

- `get_device_group_details`: Get device group information to use with device_group_id filter
- `get_device_details`: Query devices that may be affected by policies
- `run_api_endpoint`: For more advanced policy operations not covered by this tool

## See Also

- [SevOne API Documentation](https://docs.sevone.com/)
- [Alert Policy Management](https://docs.sevone.com/alert-policies)
- [Get Device Group Details Tool](./GET_DEVICE_GROUP_DETAILS_TOOL.md)

---

*Made with Bob*