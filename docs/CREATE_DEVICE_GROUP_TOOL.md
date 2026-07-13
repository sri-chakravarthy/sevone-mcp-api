# Create Device Group Tool

## Overview

The `create_device_group` tool allows you to create new device groups in the SevOne hierarchy. You can create groups at the root level or as children of existing groups by specifying either a parent ID or parent path.

## Tool Name

`create_device_group`

## Description

This tool creates a new device group in the SevOne hierarchy. You can specify:
1. Just the device group name (creates at root level)
2. Device group name with parent group ID
3. Device group name with parent group path (hierarchical path components)

The tool returns the created group's ID and details in JSON format.

## API Endpoint

- **Method**: POST
- **Endpoint**: `/api/v3/devicegroups`

## Parameters

### Required Parameters

- `name` (string): The name of the device group to create

### Optional Parameters

- `parent_id` (integer): The ID of the parent device group
- `parent_path` (array of strings): Hierarchical path to the parent group as an array of path components

**Note**: If both `parent_id` and `parent_path` are provided, `parent_id` takes precedence.

## Response Format

```json
{
  "success": true,
  "data": {
    "id": 100,
    "name": "My New Group",
    "parent_id": 10,
    "parent_path": ["All Device Groups", "West Coast", "Washington"]
  },
  "message": "Device group 'My New Group' created successfully with ID 100"
}
```

## Usage Examples

### Example 1: Create Root Level Group

Create a device group at the root level:

```json
{
  "name": "My New Group"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 100,
    "name": "My New Group"
  },
  "message": "Device group 'My New Group' created successfully with ID 100"
}
```

### Example 2: Create Group with Parent ID

Create a device group under an existing parent group using the parent's ID:

```json
{
  "name": "Child Group",
  "parent_id": 10
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 101,
    "name": "Child Group",
    "parent_id": 10
  },
  "message": "Device group 'Child Group' created successfully with ID 101"
}
```

### Example 3: Create Group with Parent Path

Create a device group using a hierarchical parent path:

```json
{
  "name": "Seattle Office",
  "parent_path": ["All Device Groups", "West Coast", "Washington"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 102,
    "name": "Seattle Office",
    "parent_path": ["All Device Groups", "West Coast", "Washington"]
  },
  "message": "Device group 'Seattle Office' created successfully with ID 102"
}
```

### Example 4: Parent ID Takes Precedence

When both `parent_id` and `parent_path` are provided, `parent_id` takes precedence:

```json
{
  "name": "Test Group",
  "parent_id": 20,
  "parent_path": ["All Device Groups", "Other"]
}
```

The group will be created under parent ID 20, and the `parent_path` will be ignored.

## Error Handling

The tool returns detailed error information if the operation fails:

```json
{
  "success": false,
  "error": "Device group name cannot be empty",
  "message": "Invalid input"
}
```

Common errors:
- Empty or whitespace-only group name
- Invalid parent group ID (group doesn't exist)
- Invalid parent path (path doesn't exist)
- API connection errors
- Insufficient permissions

## Notes

1. **Name Validation**: The group name is automatically trimmed of leading and trailing whitespace. Empty names are rejected.

2. **Parent Precedence**: If both `parent_id` and `parent_path` are provided, `parent_id` takes precedence and `parent_path` is ignored.

3. **Root Level Groups**: To create a group at the root level, simply omit both `parent_id` and `parent_path` parameters.

4. **Hierarchical Paths**: Parent paths are specified as arrays of path components. For example:
   - `["All Device Groups"]` - Root level
   - `["All Device Groups", "West Coast"]` - One level deep
   - `["All Device Groups", "West Coast", "Washington"]` - Two levels deep

5. **Group ID**: The response includes the newly created group's ID, which can be used for:
   - Creating child groups
   - Adding device group rules
   - Assigning devices to the group

6. **Duplicate Names**: SevOne may allow duplicate group names in different parts of the hierarchy. Use parent paths or IDs to ensure groups are created in the correct location.

## Workflow Tips

### Finding Parent Group IDs

If you know the parent group name but not its ID, use the `get_device_group_details` tool first:

```json
{
  "device_group_paths": [["All Device Groups", "West Coast"]]
}
```

Then use the returned ID in your `create_device_group` call.

### Creating Nested Hierarchies

To create a nested hierarchy, create groups from top to bottom:

1. Create parent group and note its ID
2. Create child group using parent's ID
3. Create grandchild group using child's ID

Example:
```json
// Step 1: Create parent
{"name": "Region A"}  // Returns ID: 100

// Step 2: Create child
{"name": "Site 1", "parent_id": 100}  // Returns ID: 101

// Step 3: Create grandchild
{"name": "Building A", "parent_id": 101}  // Returns ID: 102
```

## Related Tools

- `get_device_group_details`: Get device group information including IDs and paths
- `add_devicegroup_rules`: Add rules to automatically assign devices to the created group
- `get_device_details`: Query devices to assign to the group

## See Also

- [SevOne API Documentation](https://docs.sevone.com/)
- [Device Group Management](https://docs.sevone.com/device-groups)
- [Add Device Group Rules Tool](./ADD_DEVICEGROUP_RULES_TOOL.md)

---

*Made with Bob*