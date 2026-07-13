"""MCP tool to get alerting policy folder details from SevOne"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GetAlertingPolicyFolderDetailsTool:
    """
    MCP tool to get alerting policy folder details from SevOne
    
    This tool provides an interface to retrieve all policy folders
    from the SevOne system.
    """
    
    @property
    def name(self) -> str:
        return "get_alerting_policy_folder_details"
    
    @property
    def description(self) -> str:
        return """Get alerting policy folder details from SevOne.

This tool retrieves all policy folders in JSON format by calling the
GET /api/v3/policies/folders endpoint.

The tool returns folder information including:
- Folder ID
- Folder name
- Parent folder ID
- Whether the folder is editable

Examples:
- Get all folders: {}
- Get folders with pagination: {"page_size": 50}
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "page_size": {
                    "type": "integer",
                    "description": "Number of folders to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "additionalProperties": False
        }
    
    async def execute(
        self,
        api_client,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get alerting policy folder details operation
        
        Args:
            api_client: SevOneAPIClient instance
            page_size: Number of folders to return (default: 100, max: 1000)
        
        Returns:
            {
                "success": bool,
                "data": {
                    "folders": [
                        {
                            "id": str,
                            "name": str,
                            "parent_id": str,
                            "is_editable": bool
                        }
                    ],
                    "total_count": int
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate page_size
            if page_size < 1 or page_size > 1000:
                return {
                    "success": False,
                    "error": "page_size must be between 1 and 1000",
                    "message": "Invalid parameters"
                }
            
            # Build query parameters
            params = {
                "pagination.limit": str(page_size),
                "pagination.offset": "0"
            }
            
            logger.info(f"Querying alerting policy folders with page_size={page_size}")
            
            # Execute the API call
            endpoint = "/api/v3/policies/folders"
            result = await api_client.get(endpoint, params=params)
            
            # Parse the response
            if result and isinstance(result, dict):
                policy_folders = result.get("policyFolders", [])
                total_count = len(policy_folders)
                
                # Format the folders data
                formatted_folders = []
                for folder in policy_folders:
                    formatted_folder = {
                        "id": folder.get("id"),
                        "name": folder.get("name"),
                        "parent_id": folder.get("parentId"),
                        "is_editable": folder.get("isEditable")
                    }
                    formatted_folders.append(formatted_folder)
                
                logger.info(f"Successfully retrieved {total_count} alerting policy folders")
                
                return {
                    "success": True,
                    "data": {
                        "folders": formatted_folders,
                        "total_count": total_count
                    },
                    "message": f"Successfully retrieved {total_count} alerting policy folders"
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format from API",
                    "message": "Failed to retrieve alerting policy folders"
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error retrieving alerting policy folders: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to retrieve alerting policy folders"
            }

# Made with Bob