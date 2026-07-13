"""MCP tool to get object details from SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GetObjectDetailsTool:
    """
    MCP tool to get object details from SevOne
    
    This tool provides a convenient interface to query object information
    using various filters. It uses the /api/v3/objects/list endpoint internally.
    """
    
    @property
    def name(self) -> str:
        return "get_object_details"
    
    @property
    def description(self) -> str:
        return """Get object details from SevOne.

This tool retrieves detailed information about objects by querying with one or more of:
- Device ID
- Device name (exact or fuzzy match)
- Device group paths (hierarchical paths)
- Device metadata (namespace, attribute name, and value)
- Device name and object name combination
- Object group (class name and group name)
- Object metadata (namespace, attribute name, and value)

The tool returns comprehensive object information including:
- Object ID, name, and display name
- Device information
- Plugin information
- Object type and class
- Metadata (if requested)

Examples:
- Get objects by device ID: {"device_id": 123}
- Get objects by device name: {"device_name": "router1"}
- Get objects by device and object name: {"device_name": "router1", "object_name": "eth0"}
- Get objects by device group path: {"device_group_paths": [["All Device Groups", "West", "Seattle"]]}
- Get objects by device metadata: {"device_metadata_namespace": "System", "device_metadata_attribute": "Location", "device_metadata_value": "Building A"}
- Get objects by object group: {"object_group_class_name": "Interface", "object_group_name": "WAN Interfaces"}
- Get objects by object metadata: {"object_metadata_namespace": "Custom", "object_metadata_attribute": "Type", "object_metadata_value": "Critical"}
- Fuzzy search: {"device_name": "router*", "fuzzy_match": true}
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "integer",
                    "description": "Device ID to query objects for"
                },
                "device_name": {
                    "type": "string",
                    "description": "Device name to query objects for. Supports exact or fuzzy matching."
                },
                "object_name": {
                    "type": "string",
                    "description": "Object name to filter by (used with device_name). Supports exact or fuzzy matching."
                },
                "device_group_paths": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "description": "List of device group paths (hierarchical paths). Each path is an array of strings, e.g., [['All Device Groups', 'West', 'Seattle']]"
                },
                "device_metadata_namespace": {
                    "type": "string",
                    "description": "Device metadata namespace (requires device_metadata_attribute and device_metadata_value)"
                },
                "device_metadata_attribute": {
                    "type": "string",
                    "description": "Device metadata attribute name (requires device_metadata_namespace and device_metadata_value)"
                },
                "device_metadata_value": {
                    "type": "string",
                    "description": "Device metadata attribute value (requires device_metadata_namespace and device_metadata_attribute)"
                },
                "object_group_class_name": {
                    "type": "string",
                    "description": "Object group class name (requires object_group_name)"
                },
                "object_group_name": {
                    "type": "string",
                    "description": "Object group name (requires object_group_class_name)"
                },
                "object_metadata_namespace": {
                    "type": "string",
                    "description": "Object metadata namespace (requires object_metadata_attribute and object_metadata_value)"
                },
                "object_metadata_attribute": {
                    "type": "string",
                    "description": "Object metadata attribute name (requires object_metadata_namespace and object_metadata_value)"
                },
                "object_metadata_value": {
                    "type": "string",
                    "description": "Object metadata attribute value (requires object_metadata_namespace and object_metadata_attribute)"
                },
                "fuzzy_match": {
                    "type": "boolean",
                    "description": "Enable fuzzy matching for device and object names (supports wildcards like 'router*')",
                    "default": False
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include object metadata in the response",
                    "default": False
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of objects to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "anyOf": [
                {"required": ["device_id"]},
                {"required": ["device_name"]},
                {"required": ["device_group_paths"]},
                {
                    "required": ["device_metadata_namespace", "device_metadata_attribute", "device_metadata_value"]
                },
                {
                    "required": ["object_group_class_name", "object_group_name"]
                },
                {
                    "required": ["object_metadata_namespace", "object_metadata_attribute", "object_metadata_value"]
                }
            ]
        }
    
    async def execute(
        self,
        api_client,
        device_id: Optional[int] = None,
        device_name: Optional[str] = None,
        object_name: Optional[str] = None,
        device_group_paths: Optional[List[List[str]]] = None,
        device_metadata_namespace: Optional[str] = None,
        device_metadata_attribute: Optional[str] = None,
        device_metadata_value: Optional[str] = None,
        object_group_class_name: Optional[str] = None,
        object_group_name: Optional[str] = None,
        object_metadata_namespace: Optional[str] = None,
        object_metadata_attribute: Optional[str] = None,
        object_metadata_value: Optional[str] = None,
        fuzzy_match: bool = False,
        include_metadata: bool = False,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get object details operation
        
        Args:
            api_client: SevOneAPIClient instance
            device_id: Device ID to query
            device_name: Device name to query
            object_name: Object name to filter by
            device_group_paths: List of device group paths
            device_metadata_namespace: Device metadata namespace
            device_metadata_attribute: Device metadata attribute name
            device_metadata_value: Device metadata attribute value
            object_group_class_name: Object group class name
            object_group_name: Object group name
            object_metadata_namespace: Object metadata namespace
            object_metadata_attribute: Object metadata attribute name
            object_metadata_value: Object metadata attribute value
            fuzzy_match: Enable fuzzy matching
            include_metadata: Include metadata in response
            page_size: Number of objects per page
        
        Returns:
            {
                "success": bool,
                "data": {
                    "objects": list of object details,
                    "total_count": int
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate metadata parameters
            device_metadata_params = [device_metadata_namespace, device_metadata_attribute, device_metadata_value]
            if any(device_metadata_params) and not all(device_metadata_params):
                return {
                    "success": False,
                    "error": "All three device metadata parameters (namespace, attribute, value) must be provided together",
                    "message": "Invalid device metadata parameters"
                }
            
            object_group_params = [object_group_class_name, object_group_name]
            if any(object_group_params) and not all(object_group_params):
                return {
                    "success": False,
                    "error": "Both object group parameters (class_name, group_name) must be provided together",
                    "message": "Invalid object group parameters"
                }
            
            object_metadata_params = [object_metadata_namespace, object_metadata_attribute, object_metadata_value]
            if any(object_metadata_params) and not all(object_metadata_params):
                return {
                    "success": False,
                    "error": "All three object metadata parameters (namespace, attribute, value) must be provided together",
                    "message": "Invalid object metadata parameters"
                }
            
            # Validate that at least one filter is provided
            has_filter = any([
                device_id is not None,
                device_name is not None,
                device_group_paths is not None,
                all(device_metadata_params),
                all(object_group_params),
                all(object_metadata_params)
            ])
            
            if not has_filter:
                return {
                    "success": False,
                    "error": "At least one filter must be provided (device_id, device_name, device_group_paths, device_metadata, object_group, or object_metadata)",
                    "message": "Missing required parameters"
                }
            
            # Build the request body for /api/v3/objects/list
            request_body: Dict[str, Any] = {
                "pagination": {
                    "size": page_size
                }
            }
            
            # Add device ID filter
            if device_id is not None:
                if not request_body.get("devices"):
                    request_body["devices"] = []
                request_body["devices"].append({"device": str(device_id)})
                logger.info(f"Querying objects by device ID: {device_id}")
            
            # Add device name filter
            if device_name is not None:
                if not request_body.get("devices"):
                    request_body["devices"] = []
                device_filter = {
                    "deviceName": {
                        "value": device_name
                    }
                }
                if fuzzy_match:
                    device_filter["deviceName"]["type"] = "FUZZABLE_STRING_TYPE_FUZZY"
                request_body["devices"].append(device_filter)
                logger.info(f"Querying objects by device name: {device_name} (fuzzy={fuzzy_match})")
            
            # Add object name filter (used with device name)
            if object_name is not None:
                if not request_body.get("deviceObjects"):
                    request_body["deviceObjects"] = []
                object_filter = {
                    "objectName": {
                        "value": object_name
                    }
                }
                if fuzzy_match:
                    object_filter["objectName"]["type"] = "FUZZABLE_STRING_TYPE_FUZZY"
                
                # If device_name is also provided, combine them
                if device_name is not None:
                    object_filter["deviceName"] = {
                        "value": device_name
                    }
                    if fuzzy_match:
                        object_filter["deviceName"]["type"] = "FUZZABLE_STRING_TYPE_FUZZY"
                
                request_body["deviceObjects"].append(object_filter)
                logger.info(f"Querying objects by object name: {object_name} (fuzzy={fuzzy_match})")
            
            # Add device group paths filter
            if device_group_paths:
                request_body["deviceGroupPaths"] = [
                    {"pathComponents": path} for path in device_group_paths
                ]
                logger.info(f"Querying objects by device group paths: {device_group_paths}")
            
            # Add device metadata filter
            if all(device_metadata_params):
                if not request_body.get("deviceMetadataFilters"):
                    request_body["deviceMetadataFilters"] = []
                request_body["deviceMetadataFilters"].append({
                    "attributeName": {
                        "namespace": device_metadata_namespace,
                        "attribute": device_metadata_attribute
                    },
                    "attributeValue": device_metadata_value
                })
                logger.info(f"Querying objects by device metadata: {device_metadata_namespace}.{device_metadata_attribute}={device_metadata_value}")
            
            # Add object group filter
            if all(object_group_params):
                if not request_body.get("objectGroupNames"):
                    request_body["objectGroupNames"] = []
                request_body["objectGroupNames"].append({
                    "className": object_group_class_name,
                    "groupName": object_group_name
                })
                logger.info(f"Querying objects by object group: {object_group_class_name}.{object_group_name}")
            
            # Add object metadata filter
            if all(object_metadata_params):
                if not request_body.get("objectMetadataFilters"):
                    request_body["objectMetadataFilters"] = []
                request_body["objectMetadataFilters"].append({
                    "attributeName": {
                        "namespace": object_metadata_namespace,
                        "attribute": object_metadata_attribute
                    },
                    "attributeValue": object_metadata_value
                })
                logger.info(f"Querying objects by object metadata: {object_metadata_namespace}.{object_metadata_attribute}={object_metadata_value}")
            
            # Add metadata options if requested
            if include_metadata:
                if not request_body.get("metadataAttributes"):
                    request_body["metadataAttributes"] = []
                # Request all metadata attributes
                logger.info("Including metadata in response")
            
            # Execute the API call
            endpoint = "/api/v3/objects/list"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Extract objects from response
            objects = result.get("objects", [])
            total_count = len(objects)
            
            logger.info(f"Successfully retrieved {total_count} object(s)")
            
            return {
                "success": True,
                "data": {
                    "objects": objects,
                    "total_count": total_count
                },
                "message": f"Successfully retrieved {total_count} object(s)"
            }
            
        except Exception as e:
            logger.error(f"Failed to get object details: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get object details"
            }

# Made with Bob
