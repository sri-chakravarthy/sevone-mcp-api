# Device Group Paths Update

## Summary

Updated the `get_device_group_details` tool documentation to clarify that device group paths are NOT split by the `/` delimiter. Each path string is treated as a complete path component.

## Changes Made

### 1. Tool Description (`src/tools/get_device_group_details.py`)
- Updated the tool description to clarify that paths are "full path strings, not split by delimiter"
- Added explicit note: "Each path string is treated as a complete path and is NOT split by '/' delimiter"
- Updated example to show: `["All Device Groups/AP/IND", "All Device Groups/AP"]`

### 2. Input Schema Description
- Changed from: "List of device group paths as strings with '/' separators"
- Changed to: "List of device group paths as complete path strings (not split by delimiter)"

### 3. Test File (`tests/test_get_device_group_details.py`)
- Updated test cases to use complete path strings instead of arrays
- Changed from: `[["All Device Groups", "AP", "IND"]]`
- Changed to: `["All Device Groups/AP/IND"]`

## API Request Format

When you provide paths like:
```python
device_group_paths=["All Device Groups/AP/IND", "All Device Groups/AP"]
```

The tool generates this API request:
```json
{
  "paths": [
    {
      "pathComponents": ["All Device Groups/AP/IND"]
    },
    {
      "pathComponents": ["All Device Groups/AP"]
    }
  ]
}
```

## Key Points

1. **No Path Splitting**: The entire path string (including `/` characters) is sent as a single path component
2. **Backward Compatible**: The implementation already worked this way; only documentation was updated
3. **Consistent Behavior**: This matches the expected API behavior where each path is a complete string

## Example Usage

```python
# Correct usage
tool.execute(
    api_client,
    device_group_paths=[
        "All Device Groups/AP/IND",
        "All Device Groups/AP"
    ]
)

# This generates the correct API request:
# {
#   "paths": [
#     {"pathComponents": ["All Device Groups/AP/IND"]},
#     {"pathComponents": ["All Device Groups/AP"]}
#   ]
# }
```

## Files Modified

1. `src/tools/get_device_group_details.py` - Updated documentation and comments
2. `tests/test_get_device_group_details.py` - Updated test cases to use correct format
3. `docs/GET_DEVICE_GROUP_DETAILS_TOOL.md` - Already had correct documentation

## Testing

Run the updated tests:
```bash
python tests/test_get_device_group_details.py
```

The tests now correctly use complete path strings instead of path component arrays.