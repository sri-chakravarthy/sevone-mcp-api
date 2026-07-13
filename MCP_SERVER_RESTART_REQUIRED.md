# MCP Server Restart Required

The `get_device_group_details` tool schema has been updated to accept device group paths as strings with '/' separators instead of arrays of strings.

## Changes Made

1. **Input Schema Update**: `device_group_paths` now accepts `Array<string>` instead of `Array<Array<string>>`
   - Old format: `[["All Device Groups", "AP", "IND"]]`
   - New format: `["All Device Groups/AP/IND"]`

2. **Implementation Update**: The tool now splits path strings on '/' to create path components for the API

3. **Documentation Update**: Updated all examples and descriptions to reflect the new format

## To Apply Changes

Please restart the MCP server to load the updated tool schema:

```bash
# Stop the current MCP server process
# Then restart it with:
python src/server.py
```

## Test After Restart

```json
{
  "name": "get_device_group_details",
  "arguments": {
    "device_group_paths": ["All Device Groups/AP"],
    "include_metadata": true
  }
}
```

This will send the following JSON to the API:
```json
{
  "pagination": {
    "size": 100
  },
  "paths": [
    {
      "pathComponents": ["All Device Groups", "AP"]
    }
  ],
  "metadataAttributes": []
}