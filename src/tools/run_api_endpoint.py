"""Generic MCP tool to execute any SevOne API endpoint"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RunAPIEndpointTool:
    """
    Generic MCP tool to execute any SevOne API endpoint
    
    This tool provides a flexible interface for Bob AI to interact
    with any SevOne REST API endpoint without requiring specific
    tool implementations for each operation.
    """
    
    @property
    def name(self) -> str:
        return "run_api_endpoint"
    
    @property
    def description(self) -> str:
        return """Execute any SevOne REST API endpoint.
        
This tool allows you to call any SevOne API endpoint by specifying:
- The endpoint path (e.g., "/api/v3/devices")
- The HTTP method (GET, POST, PUT, PATCH, DELETE)
- Optional request body data
- Optional query parameters

Authentication is handled automatically using stored credentials.
The bearer token is managed transparently and refreshed when needed.

Examples:
- List devices: GET /api/v3/devices
- Create device: POST /api/v3/devices with body
- Update metadata: PUT /api/v3/entity/DEVICE/id/123/metadata
- Get device details: GET /api/v3/devices/123
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["endpoint", "method"],
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint path (e.g., '/api/v3/devices')",
                    "examples": [
                        "/api/v3/devices",
                        "/api/v3/devices/123",
                        "/api/v3/entity/DEVICE/id/123/metadata"
                    ]
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    "description": "HTTP method to use",
                    "default": "GET"
                },
                "data": {
                    "type": "object",
                    "description": "Request body data (for POST, PUT, PATCH)",
                    "default": None
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters (for GET requests)",
                    "default": None
                }
            }
        }
    
    async def execute(
        self,
        api_client,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the API endpoint
        
        Args:
            api_client: SevOneAPIClient instance
            endpoint: API endpoint path
            method: HTTP method
            data: Request body (optional)
            params: Query parameters (optional)
        
        Returns:
            {
                "success": bool,
                "data": dict | list,
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate endpoint starts with /api/v3
            if not endpoint.startswith("/api/v3"):
                return {
                    "success": False,
                    "error": "Endpoint must start with '/api/v3'",
                    "message": "Invalid endpoint path"
                }
            
            # Execute request based on method
            method = method.upper()
            
            logger.info(f"Executing {method} {endpoint}")
            
            if method == "GET":
                result = await api_client.get(endpoint, params=params)
            elif method == "POST":
                result = await api_client.post(endpoint, json_data=data or {})
            elif method == "PUT":
                result = await api_client.put(endpoint, json_data=data or {})
            elif method == "PATCH":
                result = await api_client.patch(endpoint, json_data=data or {})
            elif method == "DELETE":
                result = await api_client.delete(endpoint)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}",
                    "message": "Use GET, POST, PUT, PATCH, or DELETE"
                }
            
            logger.info(f"Successfully executed {method} {endpoint}")
            
            return {
                "success": True,
                "data": result,
                "message": f"Successfully executed {method} {endpoint}"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute {method} {endpoint}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {method} {endpoint}"
            }

# Made with Bob
