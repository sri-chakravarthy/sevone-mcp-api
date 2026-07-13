"""MCP tool to get device group details from SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GetDeviceGroupDetailsTool:
    """
    MCP tool to get device group details from SevOne
    
    This tool provides a convenient interface to query device group information
    by device group IDs or device group paths. It uses the
    /api/v3/devicegroups/list endpoint internally.
    """
    
    @property
    def name(self) -> str:
        return "get_device_group_details"
    
    @property
    def description(self) -> str:
        return """Get device group details from SevOne.

This tool retrieves detailed information about device groups by querying with one of:
- List of device group IDs
- List of device group paths (full path strings, not split by delimiter)

The tool returns comprehensive device group information including:
- Device group ID and name
- Full hierarchical path
- Maximum alert severity
- Metadata (if requested)

Examples:
- Get groups by IDs: {"device_group_ids": [10, 20]}
- Get groups by paths: {"device_group_paths": ["All Device Groups/AP/IND", "All Device Groups/AP"]}
- Get groups with metadata: {"device_group_ids": [10], "include_metadata": true}

Note: Each path string is treated as a complete path and is NOT split by '/' delimiter.
For example, "All Device Groups/AP/IND" is sent as a single path component to the API.
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_group_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device group IDs to query"
                },
                "device_group_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of device group paths as complete path strings (not split by delimiter), e.g., ['All Device Groups/AP/IND', 'All Device Groups/AP']"
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include device group metadata in the response",
                    "default": False
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of device groups to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "oneOf": [
                {"required": ["device_group_ids"]},
                {"required": ["device_group_paths"]}
            ]
        }
    
    async def execute(
        self,
        api_client,
        device_group_ids: Optional[List[int]] = None,
        device_group_paths: Optional[List[str]] = None,
        include_metadata: bool = False,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get_device_group_details tool
        
        Args:
            api_client: The SevOne API client instance
            device_group_ids: Optional list of device group IDs
            device_group_paths: Optional list of device group paths as complete path strings (not split by delimiter)
            include_metadata: Whether to include metadata in the response
            page_size: Number of device groups to return per page
            
        Returns:
            Dict containing the device group details or error information
        """
        try:
            # Validate that at least one query parameter is provided
            if not device_group_ids and not device_group_paths:
                return {
                    "success": False,
                    "error": "At least one of device_group_ids or device_group_paths must be provided",
                    "message": "Invalid input parameters"
                }
            
            # Build the request body
            request_body = {
                "pagination": {
                    "limit": page_size
                }
            }
            
            # Add device group IDs if provided
            if device_group_ids:
                request_body["ids"] = [str(id) for id in device_group_ids]
            
            # Add device group paths if provided
            if device_group_paths:
                # Each path string is a single path component, not split by "/"
                request_body["paths"] = [
                    {"pathComponents": [path]} for path in device_group_paths
                ]
            
            # Add metadata attributes if requested
            if include_metadata:
                # Request all metadata attributes by not specifying any specific ones
                # The API will return all available metadata
                request_body["metadataAttributes"] = []
            
            logger.info(f"Querying device groups with request: {request_body}")
            
            # Make the API call
            response = await api_client.post(
                "/api/v3/devicegroups/list",
                json_data=request_body
            )
            
            # The API client returns the JSON directly
            device_groups = response.get("deviceGroups", [])
            
            logger.info(f"Successfully retrieved {len(device_groups)} device groups")
            
            return {
                "status": "success",
                "device_groups": device_groups,
                "total_count": len(device_groups),
                "message": f"Successfully retrieved {len(device_groups)} device groups"
            }
                
        except Exception as e:
            logger.error(f"Error executing get_device_group_details: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "device_groups": [],
                "total_count": 0,
                "message": "An error occurred while retrieving device group details"
            }

# Made with Bob
