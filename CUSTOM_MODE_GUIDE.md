# SevOne API Expert Mode - User Guide

This guide explains how to use the custom Bob mode for SevOne API operations.

## Overview

The **SevOne API Expert** mode is a specialized Bob mode that:
- Reads the SevOne Swagger API documentation
- Understands user requests in natural language
- Determines the appropriate API endpoint and method
- Constructs proper request data
- Executes API calls via the MCP server
- Presents results clearly

## Setup

### 1. Ensure MCP Server is Running

The mode requires the SevOne MCP server to be configured in Bob:

```json
{
  "mcpServers": {
    "sevone-api": {
      "command": "python",
      "args": ["/path/to/sevone-mcp-server/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/sevone-mcp-server"
      }
    }
  }
}
```

### 2. Custom Mode is Auto-Loaded

The mode is defined in `.bob/custom_modes.yaml` and will be automatically available in Bob.

### 3. Swagger Documentation Available

The mode references `api-docs/sevone-swagger.json` for API specifications.

## How It Works

### Workflow

```
User Request
    ↓
Bob (SevOne API Expert Mode)
    ↓
1. Understand request
2. Read Swagger docs
3. Determine endpoint & method
4. Prepare request data
    ↓
run_api_endpoint tool (MCP)
    ↓
SevOne API
    ↓
Results presented to user
```

### Example Interactions

#### Example 1: List Devices

**User:** "Show me all devices"

**Mode Actions:**
1. Identifies this as a query operation
2. Reads Swagger → finds `GET /api/v3/devices`
3. Executes:
   ```
   run_api_endpoint(
     endpoint="/api/v3/devices",
     method="GET",
     params={"limit": 50}
   )
   ```
4. Presents devices in a table

**User sees:**
```
Found 45 devices:

| ID  | Name        | IP            | Status |
|-----|-------------|---------------|--------|
| 1   | Router-01   | 192.168.1.1   | Active |
| 2   | Switch-02   | 192.168.1.2   | Active |
...
```

#### Example 2: Create Device

**User:** "Create a device called 'Test-Router' with IP 10.0.0.1"

**Mode Actions:**
1. Identifies this as a creation operation
2. Reads Swagger → finds `POST /api/v3/devices` and required fields
3. Determines deviceTypeId and peerId (may ask user if needed)
4. Executes:
   ```
   run_api_endpoint(
     endpoint="/api/v3/devices",
     method="POST",
     data={
       "name": "Test-Router",
       "ip": "10.0.0.1",
       "deviceTypeId": 1,
       "peerId": 1
     }
   )
   ```
5. Confirms creation

**User sees:**
```
✓ Device created successfully!

Device Details:
- ID: 123
- Name: Test-Router
- IP: 10.0.0.1
- Status: Active
```

#### Example 3: Update Metadata

**User:** "Set the location metadata for device 123 to 'Data Center A'"

**Mode Actions:**
1. Identifies this as a metadata update
2. Reads Swagger → finds `PUT /api/v3/entity/DEVICE/id/{id}/metadata`
3. May need to query metadata namespaces/attributes first
4. Executes:
   ```
   run_api_endpoint(
     endpoint="/api/v3/entity/DEVICE/id/123/metadata",
     method="PUT",
     data={
       "metadata": [
         {
           "namespaceId": 1,
           "attributeId": 5,
           "value": "Data Center A"
         }
       ]
     }
   )
   ```
5. Confirms update

#### Example 4: Complex Multi-Step Operation

**User:** "Find all devices with 'Router' in the name and update their location to 'Building 1'"

**Mode Actions:**
1. Step 1: List devices with filter
   ```
   GET /api/v3/devices?name=*Router*
   ```
2. Step 2: For each device, update metadata
   ```
   PUT /api/v3/entity/DEVICE/id/{id}/metadata
   ```
3. Reports progress and results

**User sees:**
```
Found 5 devices matching 'Router':
1. Router-01 (ID: 10)
2. Router-02 (ID: 15)
3. Core-Router (ID: 23)
4. Edge-Router-1 (ID: 45)
5. Edge-Router-2 (ID: 46)

Updating location metadata...
✓ Router-01 updated
✓ Router-02 updated
✓ Core-Router updated
✓ Edge-Router-1 updated
✓ Edge-Router-2 updated

All 5 devices updated successfully!
```

## Common Use Cases

### Device Management

```
"List all devices"
"Show devices in peer 1"
"Create a device named X with IP Y"
"Delete device 123"
"Get details for device 456"
"Find devices with IP starting with 192.168"
```

### Metadata Operations

```
"Show metadata for device 123"
"Update location metadata for device 456 to 'NYC'"
"Set custom field 'Owner' to 'Network Team' for device 789"
"List all metadata namespaces"
"Show all metadata attributes"
```

### Alert Management

```
"List all alert policies"
"Create an alert policy for high CPU usage"
"Show active alerts"
"Get alert details for policy 123"
"Update alert threshold for policy 456"
```

### Object Management

```
"List objects for device 123"
"Show all interface objects"
"Get object details for object 456"
"Find objects with name containing 'eth0'"
```

### Discovery & Polling

```
"Trigger discovery for device 123"
"Check polling status for device 456"
"Enable polling for object 789"
"Disable polling for object 101"
```

## Tips for Best Results

### 1. Be Specific

❌ "Show me stuff"
✅ "Show me all devices in peer 1"

### 2. Provide Required Information

❌ "Create a device"
✅ "Create a device named Router-01 with IP 192.168.1.1"

### 3. Use Natural Language

The mode understands natural language:
- "List all devices"
- "Show me devices"
- "Get all devices"
- "What devices do we have?"

All work the same way!

### 4. Ask for Clarification

If the mode needs more information, it will ask:

**User:** "Create a device"
**Mode:** "I need more information to create a device:
- Device name
- IP address
- Device type ID (optional, default: 1)
- Peer ID (optional, default: 1)

Please provide these details."

### 5. Explore the API

**User:** "What can I do with devices?"
**Mode:** Will list available device operations from Swagger

**User:** "Show me the metadata API"
**Mode:** Will explain metadata endpoints and operations

## Advanced Features

### Pagination

The mode handles pagination automatically:

**User:** "Show me all devices"
**Mode:** 
- Fetches first page
- If more results exist, asks if you want to see more
- Can fetch all pages or specific ranges

### Error Handling

If an API call fails, the mode:
1. Explains what went wrong
2. Shows the error message
3. Suggests corrections
4. Offers to retry with fixes

**Example:**
```
❌ API Error: Device creation failed

Error: Missing required field 'deviceTypeId'

Suggestion: Let me retry with deviceTypeId=1 (default device type)

Would you like me to:
1. Retry with default deviceTypeId
2. Let you specify a deviceTypeId
3. Show available device types first
```

### Data Validation

The mode validates data before making API calls:
- Checks required fields
- Validates data types
- Ensures proper format
- Warns about potential issues

### Response Formatting

Results are presented in user-friendly formats:
- Tables for lists
- JSON for detailed objects
- Summaries for operations
- Charts/graphs (when applicable)

## Troubleshooting

### Mode Not Available

**Issue:** Can't find "SevOne API Expert" mode

**Solution:**
1. Check `.bob/custom_modes.yaml` exists
2. Restart Bob to reload custom modes
3. Verify YAML syntax is correct

### MCP Server Not Connected

**Issue:** "MCP server not available" error

**Solution:**
1. Check MCP server is running: `python src/server.py`
2. Verify Bob's MCP configuration
3. Check `.env` file has correct credentials
4. Review server logs for errors

### API Errors

**Issue:** API calls failing

**Solution:**
1. Check SevOne instance is accessible
2. Verify credentials in `.env`
3. Check API endpoint exists in Swagger
4. Review request data format
5. Check SevOne user permissions

### Swagger Not Found

**Issue:** "Cannot read Swagger documentation"

**Solution:**
1. Ensure `api-docs/sevone-swagger.json` exists
2. Verify file is valid JSON
3. Check file permissions

## Comparison with Direct API Calls

### Without Custom Mode

```python
# Manual approach
1. Read Swagger documentation
2. Understand endpoint structure
3. Prepare authentication
4. Construct HTTP request
5. Handle response
6. Parse and format data
```

### With Custom Mode

```
User: "List all devices"
Mode: [Handles everything automatically]
```

**Benefits:**
- ✅ No need to read Swagger manually
- ✅ No authentication handling
- ✅ Natural language interface
- ✅ Automatic error handling
- ✅ Formatted results
- ✅ Multi-step operations simplified

## Integration with Other Modes

The SevOne API Expert mode can work alongside other Bob modes:

### With Code Mode
```
User: "Generate Python code to list devices"
Mode: Switches to Code mode, generates code using SevOne API
```

### With SQL Expert Mode
```
User: "Get devices from SevOne and compare with database"
Mode: Uses both SevOne API and SQL to correlate data
```

## Best Practices

1. **Start Simple**: Begin with basic queries before complex operations
2. **Verify First**: Use GET requests to verify data before making changes
3. **Use Filters**: Apply filters to reduce result sets
4. **Check Results**: Always verify operation results
5. **Understand Errors**: Read error messages carefully
6. **Ask Questions**: The mode can explain API capabilities

## Example Session

```
User: Switch to SevOne API Expert mode

Bob: Switched to SevOne API Expert mode. I can help you with SevOne API operations.
     I have access to the Swagger documentation and the MCP server is connected.
     What would you like to do?

User: What can I do with this mode?

Bob: I can help you with:
     - Device management (list, create, update, delete)
     - Metadata operations
     - Alert policy management
     - Object queries
     - Discovery and polling
     - And much more!
     
     Try asking: "List all devices" or "Show me alert policies"

User: List all devices

Bob: [Executes API call]
     Found 127 devices. Here are the first 20:
     
     [Shows table of devices]
     
     Would you like to see more, filter by criteria, or get details on a specific device?

User: Show me devices with 'router' in the name

Bob: [Executes filtered query]
     Found 15 devices matching 'router':
     
     [Shows filtered results]

User: Get details for device ID 45

Bob: [Executes GET /api/v3/devices/45]
     
     Device Details:
     - ID: 45
     - Name: Core-Router-01
     - IP: 10.0.1.1
     - Status: Active
     - Device Type: Router
     - Peer: Primary
     - Last Discovery: 2024-01-15 10:30:00
     
     Would you like to see objects, metadata, or alerts for this device?
```

## Summary

The SevOne API Expert mode provides:
- 🎯 Natural language interface to SevOne API
- 📚 Automatic Swagger documentation reading
- 🔧 Intelligent API call construction
- ✅ Error handling and validation
- 📊 Formatted, readable results
- 🚀 Multi-step operation support

It's like having a SevOne API expert assistant that handles all the technical details for you!