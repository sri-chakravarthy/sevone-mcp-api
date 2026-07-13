# Add Device Group Rules Tool

## Overview

The `add_devicegroup_rules` tool allows you to create device group rules in SevOne that automatically assign devices to device groups based on various matching criteria.

## Tool Name

`add_devicegroup_rules`

## Description

This tool creates rules that automatically assign devices to device groups based on various matching criteria. You can specify one or more of the following rule types:

1. **Metadata-based rule**: Match devices by metadata namespace, attribute, and value
2. **Description-based rule**: Match devices by description pattern
3. **Management IP-based rule**: Match devices by management IP pattern
4. **Name-based rule**: Match devices by device name pattern
5. **sysContact-based rule**: Match devices by SNMP sysContact pattern
6. **sysDescr-based rule**: Match devices by SNMP sysDescr pattern
7. **sysLocation-based rule**: Match devices by SNMP sysLocation pattern
8. **sysName-based rule**: Match devices by SNMP sysName pattern
9. **sysObjectId-based rule**: Match devices by SNMP sysObjectId pattern

All pattern-based rules support regular expressions for flexible matching.

## API Endpoint

- **Method**: POST
- **Endpoint**: `/api/v3/devicegroups/rules`

## Parameters

### Required Parameters

- `device_group_id` (integer): The ID of the device group to add the rule to

### Optional Parameters (at least one must be provided)

#### Metadata Rule Parameters (must be provided together)
- `namespace_id` (integer): Metadata namespace ID
- `attribute_id` (integer): Metadata attribute ID
- `metadata_value_expression` (string): Regular expression to match metadata values

#### Expression-based Rule Parameters
- `description_expression` (string): Regular expression to match device description
- `mgt_ip_expression` (string): Regular expression to match management IP address
- `name_expression` (string): Regular expression to match device name
- `sys_contact_expression` (string): Regular expression to match SNMP sysContact
- `sys_descr_expression` (string): Regular expression to match SNMP sysDescr
- `sys_location_expression` (string): Regular expression to match SNMP sysLocation
- `sys_name_expression` (string): Regular expression to match SNMP sysName
- `sys_object_id_expression` (string): Regular expression to match SNMP sysObjectId

## Response Format

```json
{
  "success": true,
  "data": {
    "rule_id": 123,
    "device_group_id": 224,
    "rule_details": {
      "id": "123",
      "groupId": "224",
      "nameExpression": "router.*"
    }
  },
  "message": "Successfully created device group rule with ID: 123"
}
```

## Usage Examples

### Example 1: Metadata-based Rule

Add a rule to assign all WiFi Access Points to a device group:

```json
{
  "device_group_id": 224,
  "namespace_id": 14,
  "attribute_id": 185,
  "metadata_value_expression": "WiFi Access Point"
}
```

### Example 2: Name Pattern Rule

Add a rule to assign all devices with names starting with "router" to a device group:

```json
{
  "device_group_id": 224,
  "name_expression": "router.*"
}
```

### Example 3: Multiple Criteria Rule

Add a rule with multiple matching criteria:

```json
{
  "device_group_id": 224,
  "name_expression": "switch.*",
  "sys_location_expression": "Building A"
}
```

### Example 4: IP Address Pattern Rule

Add a rule to assign devices in a specific IP subnet:

```json
{
  "device_group_id": 224,
  "mgt_ip_expression": "10\\.52\\.0\\..*"
}
```

### Example 5: SNMP sysObjectId Rule

Add a rule to assign devices based on SNMP sysObjectId:

```json
{
  "device_group_id": 224,
  "sys_object_id_expression": "\\.1\\.3\\.6\\.1\\.4\\.1\\.9\\.1\\.1069"
}
```

## Regular Expression Tips

- Use `.*` to match any characters
- Use `\.` to match a literal dot (escape the dot)
- Use `^` to match the start of a string
- Use `$` to match the end of a string
- Use `|` for OR conditions (e.g., `router|switch`)
- Use `[0-9]` to match any digit
- Use `[a-zA-Z]` to match any letter

## Error Handling

The tool returns detailed error information if the operation fails:

```json
{
  "success": false,
  "error": "At least one matching criterion must be provided",
  "message": "Missing required parameters"
}
```

Common errors:
- Missing required `device_group_id`
- No matching criteria provided
- Incomplete metadata rule (missing namespace_id, attribute_id, or metadata_value_expression)
- Invalid device group ID
- API connection errors

## Notes

1. **Metadata Rules**: When creating a metadata-based rule, you must provide all three parameters together: `namespace_id`, `attribute_id`, and `metadata_value_expression`.

2. **Multiple Criteria**: You can combine multiple criteria in a single rule. Devices must match ALL specified criteria to be assigned to the group.

3. **Regular Expressions**: All expression fields support regular expressions. Make sure to properly escape special characters (e.g., use `\.` for a literal dot).

4. **Rule Application**: After creating a rule, you may need to apply it to existing devices using the `/api/v3/devicegroups/rules/apply` endpoint.

5. **Rule ID**: The response includes the newly created rule ID, which can be used for future operations like updating or deleting the rule.

## Related Tools

- `get_device_group_details`: Get device group information including IDs
- `get_device_metadata_ids`: Get metadata namespace and attribute IDs
- `get_device_details`: Query devices to test rule criteria

## See Also

- [SevOne API Documentation](https://docs.sevone.com/)
- [Device Group Management](https://docs.sevone.com/device-groups)
- [Regular Expression Guide](https://www.regular-expressions.info/)

---

*Made with Bob*