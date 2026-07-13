"""MCP tool to get indicator details from SevOne"""

from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class GetIndicatorDetailsTool:
    """
    MCP tool to get indicator details from SevOne
    
    This tool provides a comprehensive interface to query indicator information
    using various filters. It uses the /api/v3/metadata/indicators endpoint internally.
    """
    
    @property
    def name(self) -> str:
        return "get_indicator_details"
    
    @property
    def description(self) -> str:
        return """Get indicator details from SevOne.

This tool retrieves detailed information about indicators by querying with one or more of:
- List of device IDs
- List of device names (exact or fuzzy match)
- List of (deviceName, objectName) combinations
- List of indicator IDs
- List of indicator type IDs
- List of indicator type descriptions
- List of indicator type names
- List of object IDs
- List of object type IDs
- List of object type paths
- List of plugin IDs
- List of (deviceId, objectId, indicatorId) combinations
- Device metadata (namespace, attribute name, and value)
- Object group (class name and group name)
- Object metadata (namespace, attribute name, and value)

The tool returns comprehensive indicator information including:
- Indicator ID and type information
- Device and object associations
- Plugin information
- Indicator type names and descriptions
- Metadata (if requested)

Examples:
- Get indicators by device IDs: {"device_ids": [123, 456]}
- Get indicators by device names: {"device_names": ["router1", "switch2"]}
- Get indicators by device and object: {"device_object_pairs": [["router1", "eth0"], ["switch2", "port1"]]}
- Get indicators by indicator IDs: {"indicator_ids": [789, 101112]}
- Get indicators by indicator type IDs: {"indicator_type_ids": [5, 10]}
- Get indicators by object IDs: {"object_ids": [300, 400]}
- Get indicators by plugin IDs: {"plugin_ids": [1, 2]}
- Fuzzy search: {"device_names": ["router*"], "fuzzy_match": true}
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of device IDs to query indicators for"
                },
                "device_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of device names to query. Supports exact or fuzzy matching."
                },
                "device_object_pairs": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "maxItems": 2
                    },
                    "description": "List of [deviceName, objectName] pairs. Each pair is an array with exactly 2 strings."
                },
                "indicator_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of indicator IDs to query"
                },
                "indicator_type_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of indicator type IDs to query"
                },
                "indicator_type_descriptions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of indicator type descriptions to query"
                },
                "indicator_type_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of indicator type names to query"
                },
                "object_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of object IDs to query"
                },
                "object_type_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of object type IDs to query"
                },
                "object_type_paths": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "description": "List of object type paths (hierarchical paths). Each path is an array of strings."
                },
                "plugin_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of plugin IDs to query"
                },
                "device_object_indicator_triples": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "minItems": 3,
                        "maxItems": 3
                    },
                    "description": "List of [deviceId, objectId, indicatorId] triples. Each triple is an array with exactly 3 integers."
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
                    "description": "Enable fuzzy matching for device names, object names, and type names (supports wildcards like 'router*')",
                    "default": False
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of indicators to return per page (default: 100, max: 1000)",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            }
        }
    
    async def execute(
        self,
        api_client,
        device_ids: Optional[List[int]] = None,
        device_names: Optional[List[str]] = None,
        device_object_pairs: Optional[List[List[str]]] = None,
        indicator_ids: Optional[List[int]] = None,
        indicator_type_ids: Optional[List[int]] = None,
        indicator_type_descriptions: Optional[List[str]] = None,
        indicator_type_names: Optional[List[str]] = None,
        object_ids: Optional[List[int]] = None,
        object_type_ids: Optional[List[int]] = None,
        object_type_paths: Optional[List[List[str]]] = None,
        plugin_ids: Optional[List[int]] = None,
        device_object_indicator_triples: Optional[List[List[int]]] = None,
        device_metadata_namespace: Optional[str] = None,
        device_metadata_attribute: Optional[str] = None,
        device_metadata_value: Optional[str] = None,
        object_group_class_name: Optional[str] = None,
        object_group_name: Optional[str] = None,
        object_metadata_namespace: Optional[str] = None,
        object_metadata_attribute: Optional[str] = None,
        object_metadata_value: Optional[str] = None,
        fuzzy_match: bool = False,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get indicator details operation
        
        Returns:
            {
                "success": bool,
                "data": {
                    "indicators": list of indicator objects,
                    "total_count": int,
                    "truncated": bool (if results were truncated),
                    "truncated_message": str (if truncated)
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
                device_ids,
                device_names,
                device_object_pairs,
                indicator_ids,
                indicator_type_ids,
                indicator_type_descriptions,
                indicator_type_names,
                object_ids,
                object_type_ids,
                object_type_paths,
                plugin_ids,
                device_object_indicator_triples,
                all(device_metadata_params),
                all(object_group_params),
                all(object_metadata_params)
            ])
            
            if not has_filter:
                return {
                    "success": False,
                    "error": "At least one filter must be provided",
                    "message": "Missing required parameters"
                }
            
            # Build the request body for /api/v3/metadata/indicators
            request_body: Dict[str, Any] = {
                "pagination": {
                    "limit": str(page_size)
                }
            }
            
            # Build filters array
            filters: Dict[str, Any] = {}
            
            # Add device IDs filter
            if device_ids:
                filters["deviceIds"] = [str(id) for id in device_ids]
                logger.info(f"Querying indicators by device IDs: {device_ids}")
            
            # Add device names filter
            if device_names:
                filters["deviceNames"] = [
                    {
                        "value": name,
                        "type": "FUZZABLE_STRING_TYPE_FUZZY" if fuzzy_match else "FUZZABLE_STRING_TYPE_EXACT"
                    }
                    for name in device_names
                ]
                logger.info(f"Querying indicators by device names: {device_names} (fuzzy={fuzzy_match})")
            
            # Add device-object pairs filter
            if device_object_pairs:
                if not filters.get("deviceObjects"):
                    filters["deviceObjects"] = []
                for device_name, object_name in device_object_pairs:
                    filters["deviceObjects"].append({
                        "deviceName": {
                            "value": device_name,
                            "type": "FUZZABLE_STRING_TYPE_FUZZY" if fuzzy_match else "FUZZABLE_STRING_TYPE_EXACT"
                        },
                        "objectName": {
                            "value": object_name,
                            "type": "FUZZABLE_STRING_TYPE_FUZZY" if fuzzy_match else "FUZZABLE_STRING_TYPE_EXACT"
                        }
                    })
                logger.info(f"Querying indicators by device-object pairs: {device_object_pairs} (fuzzy={fuzzy_match})")
            
            # Add indicator IDs filter
            if indicator_ids:
                filters["indicatorIds"] = [str(id) for id in indicator_ids]
                logger.info(f"Querying indicators by indicator IDs: {indicator_ids}")
            
            # Add indicator type IDs filter
            if indicator_type_ids:
                filters["indicatorTypeIds"] = [str(id) for id in indicator_type_ids]
                logger.info(f"Querying indicators by indicator type IDs: {indicator_type_ids}")
            
            # Add indicator type descriptions filter
            if indicator_type_descriptions:
                filters["indicatorTypeDescriptions"] = [
                    {
                        "value": desc,
                        "type": "FUZZABLE_STRING_TYPE_FUZZY" if fuzzy_match else "FUZZABLE_STRING_TYPE_EXACT"
                    }
                    for desc in indicator_type_descriptions
                ]
                logger.info(f"Querying indicators by type descriptions: {indicator_type_descriptions} (fuzzy={fuzzy_match})")
            
            # Add indicator type names filter
            if indicator_type_names:
                filters["indicatorTypeNames"] = [
                    {
                        "value": name,
                        "type": "FUZZABLE_STRING_TYPE_FUZZY" if fuzzy_match else "FUZZABLE_STRING_TYPE_EXACT"
                    }
                    for name in indicator_type_names
                ]
                logger.info(f"Querying indicators by type names: {indicator_type_names} (fuzzy={fuzzy_match})")
            
            # Add object IDs filter
            if object_ids:
                filters["objectIds"] = [str(id) for id in object_ids]
                logger.info(f"Querying indicators by object IDs: {object_ids}")
            
            # Add object type IDs filter
            if object_type_ids:
                filters["objectTypeIds"] = [str(id) for id in object_type_ids]
                logger.info(f"Querying indicators by object type IDs: {object_type_ids}")
            
            # Add object type paths filter
            if object_type_paths:
                filters["objectTypePaths"] = [
                    {"pathComponents": path} for path in object_type_paths
                ]
                logger.info(f"Querying indicators by object type paths: {object_type_paths}")
            
            # Add plugin IDs filter
            if plugin_ids:
                filters["pluginIds"] = [str(id) for id in plugin_ids]
                logger.info(f"Querying indicators by plugin IDs: {plugin_ids}")
            
            # Add device-object-indicator triples filter
            if device_object_indicator_triples:
                if not request_body.get("indicators"):
                    request_body["indicators"] = []
                for device_id, object_id, indicator_id in device_object_indicator_triples:
                    request_body["indicators"].append({
                        "deviceId": str(device_id),
                        "objectId": str(object_id),
                        "indicatorId": str(indicator_id)
                    })
                logger.info(f"Querying indicators by device-object-indicator triples: {device_object_indicator_triples}")
            
            # Add device metadata filter
            if all(device_metadata_params):
                if not filters.get("deviceMetadataFilter"):
                    filters["deviceMetadataFilter"] = []
                filters["deviceMetadataFilter"].append({
                    "attributeName": {
                        "namespace": device_metadata_namespace,
                        "attribute": device_metadata_attribute
                    },
                    "attributeValue": device_metadata_value
                })
                logger.info(f"Querying indicators by device metadata: {device_metadata_namespace}.{device_metadata_attribute}={device_metadata_value}")
            
            # Add object group filter
            if all(object_group_params):
                if not filters.get("objectGroupNames"):
                    filters["objectGroupNames"] = []
                filters["objectGroupNames"].append({
                    "className": object_group_class_name,
                    "groupName": object_group_name
                })
                logger.info(f"Querying indicators by object group: {object_group_class_name}.{object_group_name}")
            
            # Add object metadata filter
            if all(object_metadata_params):
                if not request_body.get("objectMetadataFilter"):
                    request_body["objectMetadataFilter"] = []
                request_body["objectMetadataFilter"].append({
                    "attributeName": {
                        "namespace": object_metadata_namespace,
                        "attribute": object_metadata_attribute
                    },
                    "attributeValue": object_metadata_value
                })
                logger.info(f"Querying indicators by object metadata: {object_metadata_namespace}.{object_metadata_attribute}={object_metadata_value}")
            
            # Add filters to request body if any were built
            if filters:
                request_body["filters"] = [filters]
            
            # Execute the API call
            endpoint = "/api/v3/metadata/indicators"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Extract indicators from response
            indicators = result.get("indicators", [])
            total_count = len(indicators)
            
            # Check if results should be truncated for display
            max_display = 100
            truncated = total_count > max_display
            
            response_data = {
                "indicators": indicators[:max_display] if truncated else indicators,
                "total_count": total_count
            }
            
            if truncated:
                response_data["truncated"] = True
                response_data["truncated_message"] = (
                    f"Showing {max_display} of {total_count} indicators. "
                    f"Use pagination or add more filters to see specific results."
                )
                logger.warning(f"Results truncated: showing {max_display} of {total_count} indicators")
            
            logger.info(f"Successfully retrieved {total_count} indicator(s)")
            
            return {
                "success": True,
                "data": response_data,
                "message": f"Successfully retrieved {total_count} indicator(s)"
            }
            
        except Exception as e:
            logger.error(f"Failed to get indicator details: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get indicator details"
            }

# Made with Bob