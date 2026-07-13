"""MCP tool to get device details from SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GetDeviceDetailsTool:
    """
    MCP tool to get device details from SevOne
    
    This tool provides a convenient interface to query device information
    by device names, device IDs, or device group IDs. It uses the
    /api/v3/devices/list endpoint internally.
    """
    
    @property
    def name(self) -> str:
        return "get_device_details"
    
    @property
    def description(self) -> str:
        return """Get device details from SevOne.

This tool retrieves detailed information about devices by querying with one of:
- List of device names (exact or fuzzy match)
- List of device IDs
- List of device group IDs
- List of device group paths (hierarchical paths)

The tool returns comprehensive device information including:
- Device ID, name, and display name
- IP address and description
- Device class and timezone
- Alert information and severity
- Plugin information
- Metadata (if requested)
- Discovery status

Examples:
- Get devices by names: {"device_names": ["router1", "switch2"]}
- Get devices by IDs: {"device_ids": [123, 456]}
- Get devices by group IDs: {"device_group_ids": [10, 20]}
- Get devices by group paths: {"device_group_paths": [["All Device Groups", "West", "Seattle"]]}
- Get devices with metadata: {"device_names": ["router1"], "include_metadata": true}
- Fuzzy search: {"device_names": ["router*"], "fuzzy_match": true}
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of device names to query. Supports exact or fuzzy matching."
                },
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device IDs to query"
                },
                "device_group_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device group IDs to query"
                },
                "device_group_paths": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "description": "List of device group paths (hierarchical paths). Each path is an array of strings representing the path components, e.g., [['All Device Groups', 'West', 'Seattle'], ['All Device Groups', 'East']]"
                },
                "fuzzy_match": {
                    "type": "boolean",
                    "description": "Enable fuzzy matching for device names (supports wildcards like 'router*')",
                    "default": False
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include device metadata in the response",
                    "default": False
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of devices to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "oneOf": [
                {"required": ["device_names"]},
                {"required": ["device_ids"]},
                {"required": ["device_group_ids"]},
                {"required": ["device_group_paths"]}
            ]
        }
    
    async def execute(
        self,
        api_client,
        device_names: Optional[List[str]] = None,
        device_ids: Optional[List[int]] = None,
        device_group_ids: Optional[List[int]] = None,
        device_group_paths: Optional[List[List[str]]] = None,
        fuzzy_match: bool = False,
        include_metadata: bool = False,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get device details operation
        
        Args:
            api_client: SevOneAPIClient instance
            device_names: List of device names to query
            device_ids: List of device IDs to query
            device_group_ids: List of device group IDs to query
            device_group_paths: List of device group paths (hierarchical paths)
            fuzzy_match: Enable fuzzy matching for device names
            include_metadata: Include device metadata in response
            page_size: Number of devices per page
        
        Returns:
            {
                "success": bool,
                "data": {
                    "devices": list of device objects,
                    "total_count": int
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate that at least one filter is provided
            if not device_names and not device_ids and not device_group_ids and not device_group_paths:
                return {
                    "success": False,
                    "error": "At least one of device_names, device_ids, device_group_ids, or device_group_paths must be provided",
                    "message": "Missing required parameters"
                }
            
            # Build the request body for /api/v3/devices/list
            request_body = {
                "request": {
                    "pagination": {
                        "size": page_size
                    }
                }
            }
            
            # Add device names filter
            if device_names:
                request_body["request"]["deviceNames"] = [
                    {
                        "value": name,
                        "isFuzzy": fuzzy_match
                    }
                    for name in device_names
                ]
                logger.info(f"Querying devices by names: {device_names} (fuzzy={fuzzy_match})")
            
            # Add device IDs filter
            if device_ids:
                request_body["request"]["deviceIds"] = [str(id) for id in device_ids]
                logger.info(f"Querying devices by IDs: {device_ids}")
            
            # Add device group IDs filter
            if device_group_ids:
                request_body["request"]["deviceGroupIds"] = [str(id) for id in device_group_ids]
                logger.info(f"Querying devices by group IDs: {device_group_ids}")
            
            # Add device group paths filter
            if device_group_paths:
                request_body["request"]["deviceGroupPaths"] = [
                    {"pathComponents": path} for path in device_group_paths
                ]
                logger.info(f"Querying devices by group paths: {device_group_paths}")
            
            # Add metadata options if requested
            if include_metadata:
                request_body["request"]["metadataOptions"] = {
                    "includeMetadata": True
                }
            
            # Execute the API call
            endpoint = "/api/v3/devices/list"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Extract devices from response
            devices = result.get("devices", [])
            total_count = len(devices)
            
            logger.info(f"Successfully retrieved {total_count} device(s)")
            
            return {
                "success": True,
                "data": {
                    "devices": devices,
                    "total_count": total_count
                },
                "message": f"Successfully retrieved {total_count} device(s)"
            }
            
        except Exception as e:
            logger.error(f"Failed to get device details: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get device details"
            }

# Made with Bob