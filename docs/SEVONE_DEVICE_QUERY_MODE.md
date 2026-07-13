# SevOne Device Query Mode

## Overview

The **SevOne Device Query** mode (`sevone-device-query`) is a specialized Bob mode designed to help users easily query device information from SevOne NMS using the `get_device_details` MCP tool.

## When to Use This Mode

Use this mode when you need to:
- Find devices by name (exact or fuzzy match)
- Look up devices by device ID
- Query devices in a specific device group
- Get detailed device information including metadata
- Search for devices with wildcards (e.g., "router*")
- Retrieve device attributes like IP, class, timezone, alerts, etc.

## How It Works

This mode acts as an intelligent interface to the `get_device_details` MCP tool. It:
1. Understands your natural language query
2. Translates it into proper tool parameters
3. Executes the query via the MCP tool
4. Presents results in a clear, organized format

## Query Examples

### Find a Device by Name

**User Input:**
```
Find device router1
```

**What Bob Does:**
- Calls `get_device_details` with `device_names=["router1"]`
- Returns device details including ID, IP, status, etc.

### Search with Wildcards

**User Input:**
```
Show me all routers
```

**What Bob Does:**
- Calls `get_device_details` with `device_names=["router*"]` and `fuzzy_match=true`
- Returns all devices matching the pattern

### Query by Device ID

**User Input:**
```
Get device with ID 123
```

**What Bob Does:**
- Calls `get_device_details` with `device_ids=[123]`
- Returns the specific device information

### Query by Device Group

**User Input:**
```
List devices in group 10
```

**What Bob Does:**
- Calls `get_device_details` with `device_group_ids=[10]`
- Returns all devices in that group

### Get Device with Metadata

**User Input:**
```
Find switch2 with metadata
```

**What Bob Does:**
- Calls `get_device_details` with `device_names=["switch2"]` and `include_metadata=true`
- Returns device details plus all metadata

### Query Multiple Devices

**User Input:**
```
Show devices router1 and switch2
```

**What Bob Does:**
- Calls `get_device_details` with `device_names=["router1", "switch2"]`
- Returns information for both devices

## Available Parameters

The mode supports all parameters of the `get_device_details` tool:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `device_names` | Array of strings | Device names to query | `["router1", "switch2"]` |
| `device_ids` | Array of integers | Device IDs to query | `[123, 456]` |
| `device_group_ids` | Array of integers | Device group IDs | `[10, 20]` |
| `fuzzy_match` | Boolean | Enable wildcard matching | `true` for "router*" |
| `include_metadata` | Boolean | Include device metadata | `true` |
| `page_size` | Integer | Results per page (max 1000) | `100` |

**Note:** At least ONE of `device_names`, `device_ids`, or `device_group_ids` must be provided.

## Device Information Returned

The mode returns comprehensive device information including:

- **Basic Info**: Device ID, name, display name
- **Network**: IP address, description
- **Configuration**: Device class, timezone
- **Status**: Alert information, severity
- **Plugins**: Plugin information
- **Discovery**: Discovery status
- **Metadata**: Custom metadata (when requested)

## Tips for Best Results

1. **Use Fuzzy Matching**: When you're not sure of exact device names, use wildcards like "router*"
2. **Request Metadata**: Add "with metadata" to your query when you need detailed information
3. **Multiple Devices**: You can query multiple devices at once by listing them
4. **Be Specific**: The more specific your query, the faster and more accurate the results

## Switching to This Mode

To use this mode, you can:
1. Ask Bob to switch: "Switch to SevOne Device Query mode"
2. Use the mode selector in the Bob interface
3. Start your query with a device-related question, and Bob may suggest this mode

## Example Session

```
User: Switch to SevOne Device Query mode

Bob: Switched to 🔍 SevOne Device Query mode. I can help you query device information 
from SevOne. What devices would you like to find?

User: Find all devices starting with "core"

Bob: [Executes get_device_details with device_names=["core*"], fuzzy_match=true]

Found 3 devices:

| ID  | Name        | IP Address    | Status | Alerts |
|-----|-------------|---------------|--------|--------|
| 101 | core-rtr-01 | 10.0.1.1     | Active | 0      |
| 102 | core-rtr-02 | 10.0.1.2     | Active | 2      |
| 103 | core-sw-01  | 10.0.2.1     | Active | 0      |

User: Show me details for device 101 with metadata

Bob: [Executes get_device_details with device_ids=[101], include_metadata=true]

Device Details for core-rtr-01 (ID: 101):
- IP Address: 10.0.1.1
- Device Class: Router
- Timezone: America/New_York
- Status: Active
- Alerts: 0 active alerts

Metadata:
- Location: Data Center 1
- Owner: Network Team
- Maintenance Window: Sunday 2-4 AM
```

## Related Modes

- **SevOne API Expert** (`sevone-api-expert`): For more complex API operations beyond device queries
- **Advanced** (`advanced`): For general development tasks with MCP tool access

## Troubleshooting

**No devices found?**
- Try using fuzzy matching with wildcards
- Check if the device name is spelled correctly
- Verify the device exists in SevOne

**Need more information?**
- Add `include_metadata=true` to your query
- Ask for specific device attributes

**Query too slow?**
- Reduce the page_size parameter
- Be more specific with device names or IDs

## Technical Details

- **Mode Slug**: `sevone-device-query`
- **MCP Server**: `sevone-api`
- **MCP Tool**: `get_device_details`
- **API Endpoint**: `/api/v3/devices/list` (used internally)

---

*This mode is part of the SevOne MCP Server project and requires the sevone-api MCP server to be configured and connected.*