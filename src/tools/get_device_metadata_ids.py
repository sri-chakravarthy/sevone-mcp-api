"""MCP tool to get device metadata IDs from SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GetDeviceMetadataIdsTool:
    """
    MCP tool to get device metadata namespace and attribute IDs from SevOne
    
    This tool provides a convenient interface to query metadata information
    by device IDs, namespace and attribute names. It uses the
    /api/v3/metadata/devices/metadata endpoint internally.
    """
    
    @property
    def name(self) -> str:
        return "get_device_metadata_ids"
    
    @property
    def description(self) -> str:
        return """Get device metadata namespace and attribute IDs from SevOne.

This tool retrieves metadata information including namespace IDs and attribute IDs
by querying with one of:
- List of device IDs (entityIds)
- Namespace and attribute name combination

The tool returns metadata details in JSON format including:
- Namespace ID and name
- Attribute ID, name, and type
- Attribute values (if any)
- Entity types the attribute applies to
- Validation expressions

Examples:
- Get metadata for specific devices: {"device_ids": [123, 456]}
- Get specific attribute: {"namespace": "System", "attribute_name": "Location"}
- Get metadata for devices with specific attribute: {"device_ids": [123], "namespace": "Custom", "attribute_name": "Site"}
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device IDs (entityIds) to query metadata for"
                },
                "namespace": {
                    "type": "string",
                    "description": "Metadata namespace name to filter by"
                },
                "attribute_name": {
                    "type": "string",
                    "description": "Metadata attribute name to filter by (requires namespace)"
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of results to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "anyOf": [
                {"required": ["device_ids"]},
                {"required": ["namespace", "attribute_name"]}
            ]
        }
    
    async def execute(
        self,
        api_client,
        device_ids: Optional[List[int]] = None,
        namespace: Optional[str] = None,
        attribute_name: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get device metadata IDs operation
        
        Args:
            api_client: SevOneAPIClient instance
            device_ids: List of device IDs to query metadata for
            namespace: Metadata namespace name
            attribute_name: Metadata attribute name (requires namespace)
            page_size: Number of results per page
        
        Returns:
            {
                "success": bool,
                "data": {
                    "devices": dict of device metadata,
                    "total_devices": int
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate input combinations
            if not device_ids and not (namespace and attribute_name):
                return {
                    "success": False,
                    "error": "Either device_ids or both namespace and attribute_name must be provided",
                    "message": "Missing required parameters"
                }
            
            if attribute_name and not namespace:
                return {
                    "success": False,
                    "error": "attribute_name requires namespace to be specified",
                    "message": "Invalid parameter combination"
                }
            
            # Build the request body for /api/v3/metadata/devices/metadata
            request_body = {
                "pagination": {
                    "limit": str(page_size)
                }
            }
            
            # Add device IDs filter (entityIds)
            if device_ids:
                request_body["entityIds"] = [str(id) for id in device_ids]
                logger.info(f"Querying metadata for device IDs: {device_ids}")
            
            # Add namespace and attribute name filter
            if namespace and attribute_name:
                request_body["attributeName"] = {
                    "namespace": namespace,
                    "attribute": attribute_name
                }
                logger.info(f"Filtering by namespace: {namespace}, attribute: {attribute_name}")
            elif namespace:
                # If only namespace is provided (though schema doesn't require this)
                request_body["attributeName"] = {
                    "namespace": namespace
                }
                logger.info(f"Filtering by namespace: {namespace}")
            
            # Execute the API call
            endpoint = "/api/v3/metadata/devices/metadata"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Extract devices metadata from response
            devices_metadata = result.get("devices", {})
            total_devices = len(devices_metadata)
            
            # Process the response to extract namespace and attribute IDs
            processed_data = {}
            for device_id, device_data in devices_metadata.items():
                namespaces = device_data.get("namespaces", {})
                processed_device = {
                    "device_id": device_id,
                    "device_name": device_data.get("device", {}).get("name", ""),
                    "namespaces": {}
                }
                
                for ns_name, ns_data in namespaces.items():
                    namespace_info = {
                        "namespace_id": ns_data.get("id"),
                        "namespace_name": ns_data.get("name"),
                        "attributes": {}
                    }
                    
                    attributes = ns_data.get("attributes", {})
                    for attr_name, attr_data in attributes.items():
                        namespace_info["attributes"][attr_name] = {
                            "attribute_id": attr_data.get("id"),
                            "attribute_name": attr_data.get("name"),
                            "attribute_type": attr_data.get("type"),
                            "values": attr_data.get("values", {}),
                            "entity_types": attr_data.get("entityTypes", []),
                            "singleton": attr_data.get("singleton", False),
                            "validation_expression": attr_data.get("validationExpression", "")
                        }
                    
                    processed_device["namespaces"][ns_name] = namespace_info
                
                processed_data[device_id] = processed_device
            
            logger.info(f"Successfully retrieved metadata for {total_devices} device(s)")
            
            return {
                "success": True,
                "data": {
                    "devices": processed_data,
                    "total_devices": total_devices,
                    "raw_response": devices_metadata  # Include raw response for reference
                },
                "message": f"Successfully retrieved metadata for {total_devices} device(s)"
            }
            
        except Exception as e:
            logger.error(f"Failed to get device metadata IDs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get device metadata IDs"
            }

# Made with Bob