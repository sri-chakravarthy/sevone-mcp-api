"""MCP tool to create device groups in SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class CreateDeviceGroupTool:
    """
    MCP tool to create device groups in SevOne
    
    This tool provides an interface to create new device groups in the SevOne hierarchy.
    You can specify the group name and optionally its parent using either parent ID or parent path.
    """
    
    @property
    def name(self) -> str:
        return "create_device_group"
    
    @property
    def description(self) -> str:
        return """Create a device group in SevOne.

This tool creates a new device group in the SevOne hierarchy. You can specify:
1. Just the device group name (creates at root level)
2. Device group name with parent group ID
3. Device group name with parent group path (hierarchical path components)

The tool returns the created group's ID and details in JSON format.

Examples:
- Create root level group: {
    "name": "My New Group"
  }
- Create with parent ID: {
    "name": "Child Group",
    "parent_id": 10
  }
- Create with parent path: {
    "name": "Seattle Office",
    "parent_path": ["All Device Groups", "West Coast", "Washington"]
  }

Note: If both parent_id and parent_path are provided, parent_id takes precedence.
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the device group to create (required)"
                },
                "parent_id": {
                    "type": "integer",
                    "description": "The ID of the parent device group (optional)"
                },
                "parent_path": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Hierarchical path to the parent group as an array of path components, e.g., ['All Device Groups', 'West', 'Seattle'] (optional)"
                }
            },
            "required": ["name"],
            "additionalProperties": False
        }
    
    async def execute(
        self,
        api_client,
        name: str,
        parent_id: Optional[int] = None,
        parent_path: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute the create device group operation
        
        Args:
            api_client: SevOneAPIClient instance
            name: The name of the device group to create
            parent_id: Optional parent device group ID
            parent_path: Optional parent device group path as list of path components
        
        Returns:
            {
                "success": bool,
                "data": {
                    "id": int,
                    "name": str,
                    "parent_id": int (if applicable),
                    "parent_path": list (if applicable)
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate input
            if not name or not name.strip():
                return {
                    "success": False,
                    "error": "Device group name cannot be empty",
                    "message": "Invalid input"
                }
            
            # Build the request body for POST /api/v3/devicegroups
            request_body: Dict[str, Any] = {
                "name": name.strip()
            }
            
            # Add parent_id if provided (takes precedence over parent_path)
            if parent_id is not None:
                request_body["parentId"] = parent_id
            # Add parent_path if provided and parent_id is not set
            elif parent_path is not None and len(parent_path) > 0:
                request_body["parentPath"] = {
                    "pathComponents": parent_path
                }
            
            logger.info(f"Creating device group with request: {request_body}")
            
            # Make the API call
            response = await api_client.post(
                endpoint="/api/v3/devicegroups",
                data=request_body
            )
            
            # Extract the response data
            if response and isinstance(response, dict):
                result_data = {
                    "id": response.get("id"),
                    "name": response.get("name")
                }
                
                # Add parent information if present in response
                if "parentId" in response:
                    result_data["parent_id"] = response["parentId"]
                
                if "parentPath" in response and isinstance(response["parentPath"], dict):
                    parent_path_components = response["parentPath"].get("pathComponents", [])
                    if parent_path_components:
                        result_data["parent_path"] = parent_path_components
                
                logger.info(f"Successfully created device group: {result_data}")
                
                return {
                    "success": True,
                    "data": result_data,
                    "message": f"Device group '{name}' created successfully with ID {result_data['id']}"
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format from API",
                    "message": "Failed to create device group"
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating device group: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to create device group"
            }

# Made with Bob
