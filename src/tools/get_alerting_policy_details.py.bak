"""MCP tool to get alerting policy details from SevOne"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GetAlertingPolicyDetailsTool:
    """
    MCP tool to get alerting policy details from SevOne
    
    This tool provides an interface to query alerting policies by various criteria
    including name, alert severities, policy IDs, device group ID, and enabled/disabled status.
    """
    
    @property
    def name(self) -> str:
        return "get_alerting_policy_details"
    
    @property
    def description(self) -> str:
        return """Get alerting policy details from SevOne.

This tool retrieves detailed information about alerting policies by querying with one or more of:
- Policy name (supports fuzzy matching)
- List of alert severities (subset of EMERGENCY, CRITICAL, ERROR, WARNING)
- List of policy IDs
- List of folder IDs
- Device group ID
- Enabled/Disabled status

The tool returns comprehensive policy information including:
- Policy ID, name, and description
- Alert severity
- Enabled/disabled status
- Device group association
- Policy type and configuration
- Trigger and clear expressions
- Last updated timestamp

Examples:
- Get policy by name: {"name": "High CPU Alert"}
- Get policies by severities: {"alert_severities": ["CRITICAL", "ERROR"]}
- Get policies by IDs: {"policy_ids": [123, 456]}
- Get policies by folder IDs: {"folder_ids": [1, 2]}
- Get policies for device group: {"device_group_id": 10}
- Get enabled policies: {"is_enabled": true}
- Get disabled policies: {"is_enabled": false}
- Combined filters: {"alert_severities": ["CRITICAL"], "is_enabled": true, "device_group_id": 10}

Note: Multiple filters can be combined. Policies must match ALL specified criteria.
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Policy name to search for (supports fuzzy matching)"
                },
                "alert_severities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["EMERGENCY", "CRITICAL", "ERROR", "WARNING"]
                    },
                    "description": "List of alert severities to filter by (subset of EMERGENCY, CRITICAL, ERROR, WARNING)"
                },
                "policy_ids": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of policy IDs to query"
                },
                "folder_ids": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of folder IDs to filter policies by"
                },
                "device_group_id": {
                    "type": "integer",
                    "description": "Device group ID to filter policies by"
                },
                "is_enabled": {
                    "type": "boolean",
                    "description": "Filter by enabled (true) or disabled (false) status"
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of policies to return per page (default: 100, max: 1000)",
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
        name: Optional[str] = None,
        alert_severities: Optional[List[str]] = None,
        policy_ids: Optional[List[int]] = None,
        folder_ids: Optional[List[int]] = None,
        device_group_id: Optional[int] = None,
        is_enabled: Optional[bool] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Execute the get alerting policy details operation
        
        Args:
            api_client: SevOneAPIClient instance
            name: Policy name to search for (fuzzy matching supported)
            alert_severities: List of alert severities to filter by
            policy_ids: List of policy IDs to query
            folder_ids: List of folder IDs to filter by
            device_group_id: Device group ID to filter by
            is_enabled: Filter by enabled/disabled status
            page_size: Number of policies to return (default: 100, max: 1000)
        
        Returns:
            {
                "success": bool,
                "data": {
                    "policies": [
                        {
                            "id": int,
                            "name": str,
                            "description": str,
                            "severity": str,
                            "is_enabled": bool,
                            "is_device_group": bool,
                            "device_group_id": int (if applicable),
                            "policy_type": str,
                            "trigger_expression": str,
                            "clear_expression": str,
                            "last_updated": str,
                            ...
                        }
                    ],
                    "total_count": int
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate that at least one filter criterion is provided
            has_filter = any([
                name is not None,
                alert_severities is not None and len(alert_severities) > 0,
                policy_ids is not None and len(policy_ids) > 0,
                folder_ids is not None and len(folder_ids) > 0,
                device_group_id is not None,
                is_enabled is not None
            ])
            
            if not has_filter:
                return {
                    "success": False,
                    "error": "At least one filter criterion must be provided (name, alert_severities, policy_ids, folder_ids, device_group_id, or is_enabled)",
                    "message": "Missing required parameters"
                }
            
            # Validate alert severities if provided
            valid_severities = ["EMERGENCY", "CRITICAL", "ERROR", "WARNING"]
            if alert_severities:
                invalid_severities = [s for s in alert_severities if s not in valid_severities]
                if invalid_severities:
                    return {
                        "success": False,
                        "error": f"Invalid alert severities: {invalid_severities}. Must be subset of {valid_severities}",
                        "message": "Invalid parameters"
                    }
            
            # Validate page_size
            if page_size < 1 or page_size > 1000:
                return {
                    "success": False,
                    "error": "page_size must be between 1 and 1000",
                    "message": "Invalid parameters"
                }
            
            # Build the request body for POST /api/v3/policies/filter
            request_body: Dict[str, Any] = {
                "pagination": {
                    "limit": str(page_size),
                    "offset": "0"
                }
            }
            
            # Add name filter if provided (with fuzzy matching)
            if name is not None:
                request_body["name"] = {
                    "value": name,
                    "isFuzzy": True
                }
            
            # Add alert severities filter if provided
            if alert_severities is not None and len(alert_severities) > 0:
                request_body["alertSeverities"] = alert_severities
            
            # Add policy IDs filter if provided
            if policy_ids is not None and len(policy_ids) > 0:
                request_body["ids"] = policy_ids
            
            # Add folder IDs filter if provided
            if folder_ids is not None and len(folder_ids) > 0:
                request_body["folderIds"] = folder_ids
            
            # Add device group ID filter if provided
            if device_group_id is not None:
                request_body["groupId"] = device_group_id
            
            # Add enabled/disabled filter if provided
            if is_enabled is not None:
                request_body["isEnabled"] = "MATCH_TRUE" if is_enabled else "MATCH_FALSE"
            
            logger.info(f"Querying alerting policies with filters: name={name}, severities={alert_severities}, ids={policy_ids}, folder_ids={folder_ids}, group_id={device_group_id}, enabled={is_enabled}")
            logger.debug(f"Request body: {request_body}")
            
            # Execute the API call
            endpoint = "/api/v3/policies/filter"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Parse the response
            if result and isinstance(result, dict):
                policies = result.get("policies", [])
                total_count = len(policies)
                
                # Format the policies data
                formatted_policies = []
                for policy in policies:
                    formatted_policy = {
                        "id": policy.get("id"),
                        "name": policy.get("name"),
                        "description": policy.get("description"),
                        "severity": policy.get("severity"),
                        "is_enabled": policy.get("userEnabled"),
                        "is_device_group": policy.get("isDeviceGroup"),
                        "policy_type": policy.get("type"),
                        "trigger_expression": policy.get("triggerExpression"),
                        "clear_expression": policy.get("clearExpression"),
                        "last_updated": policy.get("lastUpdated"),
                        "folder_id": policy.get("folderId"),
                        "object_type_id": policy.get("objectTypeId"),
                        "object_sub_type_id": policy.get("objectSubTypeId")
                    }
                    
                    # Add device group ID if it's a device group policy
                    if policy.get("isDeviceGroup") and "groupId" in policy:
                        formatted_policy["device_group_id"] = policy.get("groupId")
                    
                    formatted_policies.append(formatted_policy)
                
                logger.info(f"Successfully retrieved {total_count} alerting policies")
                
                return {
                    "success": True,
                    "data": {
                        "policies": formatted_policies,
                        "total_count": total_count
                    },
                    "message": f"Successfully retrieved {total_count} alerting policies"
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format from API",
                    "message": "Failed to retrieve alerting policies"
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error retrieving alerting policies: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "message": "Failed to retrieve alerting policies"
            }

# Made with Bob
