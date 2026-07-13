"""MCP tool to add device group rules to SevOne"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AddDeviceGroupRulesTool:
    """
    MCP tool to add device group rules to SevOne
    
    This tool provides an interface to create device group rules that automatically
    assign devices to groups based on various criteria such as metadata, device name,
    IP address, SNMP attributes, etc.
    """
    
    @property
    def name(self) -> str:
        return "add_devicegroup_rules"
    
    @property
    def description(self) -> str:
        return """Add device group rules to SevOne.

This tool creates rules that automatically assign devices to device groups based on
various matching criteria. You can specify one or more of the following rule types:

1. Metadata-based rule: Match devices by metadata namespace, attribute, and value
2. Description-based rule: Match devices by description pattern
3. Management IP-based rule: Match devices by management IP pattern
4. Name-based rule: Match devices by device name pattern
5. sysContact-based rule: Match devices by SNMP sysContact pattern
6. sysDescr-based rule: Match devices by SNMP sysDescr pattern
7. sysLocation-based rule: Match devices by SNMP sysLocation pattern
8. sysName-based rule: Match devices by SNMP sysName pattern
9. sysObjectId-based rule: Match devices by SNMP sysObjectId pattern

All pattern-based rules support regular expressions for flexible matching.

Examples:
- Metadata rule: {
    "device_group_id": 224,
    "namespace_id": 14,
    "attribute_id": 185,
    "metadata_value_expression": "WiFi Access Point"
  }
- Name pattern rule: {
    "device_group_id": 224,
    "name_expression": "router.*"
  }
- Multiple criteria: {
    "device_group_id": 224,
    "name_expression": "switch.*",
    "sys_location_expression": "Building A"
  }
"""
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_group_id": {
                    "type": "integer",
                    "description": "The ID of the device group to add the rule to (required)"
                },
                "namespace_id": {
                    "type": "integer",
                    "description": "Metadata namespace ID (required for metadata-based rules)"
                },
                "attribute_id": {
                    "type": "integer",
                    "description": "Metadata attribute ID (required for metadata-based rules)"
                },
                "metadata_value_expression": {
                    "type": "string",
                    "description": "Regular expression to match metadata values (required for metadata-based rules)"
                },
                "description_expression": {
                    "type": "string",
                    "description": "Regular expression to match device description"
                },
                "mgt_ip_expression": {
                    "type": "string",
                    "description": "Regular expression to match management IP address"
                },
                "name_expression": {
                    "type": "string",
                    "description": "Regular expression to match device name"
                },
                "sys_contact_expression": {
                    "type": "string",
                    "description": "Regular expression to match SNMP sysContact"
                },
                "sys_descr_expression": {
                    "type": "string",
                    "description": "Regular expression to match SNMP sysDescr"
                },
                "sys_location_expression": {
                    "type": "string",
                    "description": "Regular expression to match SNMP sysLocation"
                },
                "sys_name_expression": {
                    "type": "string",
                    "description": "Regular expression to match SNMP sysName"
                },
                "sys_object_id_expression": {
                    "type": "string",
                    "description": "Regular expression to match SNMP sysObjectId"
                }
            },
            "required": ["device_group_id"],
            "additionalProperties": False
        }
    
    async def execute(
        self,
        api_client,
        device_group_id: int,
        namespace_id: Optional[int] = None,
        attribute_id: Optional[int] = None,
        metadata_value_expression: Optional[str] = None,
        description_expression: Optional[str] = None,
        mgt_ip_expression: Optional[str] = None,
        name_expression: Optional[str] = None,
        sys_contact_expression: Optional[str] = None,
        sys_descr_expression: Optional[str] = None,
        sys_location_expression: Optional[str] = None,
        sys_name_expression: Optional[str] = None,
        sys_object_id_expression: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the add device group rule operation
        
        Args:
            api_client: SevOneAPIClient instance
            device_group_id: The device group ID to add the rule to
            namespace_id: Metadata namespace ID (for metadata rules)
            attribute_id: Metadata attribute ID (for metadata rules)
            metadata_value_expression: Regex for metadata value matching
            description_expression: Regex for description matching
            mgt_ip_expression: Regex for management IP matching
            name_expression: Regex for device name matching
            sys_contact_expression: Regex for sysContact matching
            sys_descr_expression: Regex for sysDescr matching
            sys_location_expression: Regex for sysLocation matching
            sys_name_expression: Regex for sysName matching
            sys_object_id_expression: Regex for sysObjectId matching
        
        Returns:
            {
                "success": bool,
                "data": {
                    "rule_id": int,
                    "device_group_id": int,
                    "rule_details": dict
                },
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate that at least one matching criterion is provided
            has_metadata_rule = namespace_id is not None and attribute_id is not None and metadata_value_expression is not None
            has_other_rule = any([
                description_expression,
                mgt_ip_expression,
                name_expression,
                sys_contact_expression,
                sys_descr_expression,
                sys_location_expression,
                sys_name_expression,
                sys_object_id_expression
            ])
            
            if not has_metadata_rule and not has_other_rule:
                return {
                    "success": False,
                    "error": "At least one matching criterion must be provided (metadata rule requires namespace_id, attribute_id, and metadata_value_expression together; or provide at least one expression field)",
                    "message": "Missing required parameters"
                }
            
            # Validate metadata rule completeness
            metadata_fields = [namespace_id, attribute_id, metadata_value_expression]
            metadata_provided = [f for f in metadata_fields if f is not None]
            if len(metadata_provided) > 0 and len(metadata_provided) < 3:
                return {
                    "success": False,
                    "error": "For metadata-based rules, namespace_id, attribute_id, and metadata_value_expression must all be provided together",
                    "message": "Incomplete metadata rule parameters"
                }
            
            # Build the request body for /api/v3/devicegroups/rules
            request_body = {
                "groupId": str(device_group_id)
            }
            
            # Add metadata rule fields if provided
            if namespace_id is not None:
                request_body["namespaceId"] = str(namespace_id)
            if attribute_id is not None:
                request_body["attributeId"] = str(attribute_id)
            if metadata_value_expression is not None:
                request_body["metadataValueExpression"] = metadata_value_expression
            
            # Add expression fields if provided
            if description_expression is not None:
                request_body["descriptionExpression"] = description_expression
            if mgt_ip_expression is not None:
                request_body["mgtIpExpression"] = mgt_ip_expression
            if name_expression is not None:
                request_body["nameExpression"] = name_expression
            if sys_contact_expression is not None:
                request_body["sysContactExpression"] = sys_contact_expression
            if sys_descr_expression is not None:
                request_body["sysDescrExpression"] = sys_descr_expression
            if sys_location_expression is not None:
                request_body["sysLocationExpression"] = sys_location_expression
            if sys_name_expression is not None:
                request_body["sysNameExpression"] = sys_name_expression
            if sys_object_id_expression is not None:
                request_body["sysObjectIdExpression"] = sys_object_id_expression
            
            logger.info(f"Creating device group rule for group ID {device_group_id}")
            logger.debug(f"Rule criteria: {request_body}")
            
            # Execute the API call
            endpoint = "/api/v3/devicegroups/rules"
            result = await api_client.post(endpoint, json_data=request_body)
            
            # Extract rule ID from response
            rule_id = result.get("id")
            
            logger.info(f"Successfully created device group rule with ID: {rule_id}")
            
            return {
                "success": True,
                "data": {
                    "rule_id": int(rule_id) if rule_id else None,
                    "device_group_id": device_group_id,
                    "rule_details": result
                },
                "message": f"Successfully created device group rule with ID: {rule_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to add device group rule: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add device group rule"
            }

# Made with Bob