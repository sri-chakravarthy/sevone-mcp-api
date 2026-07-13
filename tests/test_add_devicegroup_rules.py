"""Tests for add_devicegroup_rules tool"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import AsyncMock, MagicMock
from tools.add_devicegroup_rules import AddDeviceGroupRulesTool


@pytest.fixture
def mock_api_client():
    """Create a mock API client"""
    client = MagicMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def tool():
    """Create tool instance"""
    return AddDeviceGroupRulesTool()


@pytest.mark.asyncio
async def test_add_metadata_rule(mock_api_client, tool):
    """Test adding a metadata-based device group rule"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": "123",
        "groupId": "224",
        "namespaceId": "14",
        "attributeId": "185",
        "metadataValueExpression": "WiFi Access Point"
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_group_id=224,
        namespace_id=14,
        attribute_id=185,
        metadata_value_expression="WiFi Access Point"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["rule_id"] == 123
    assert result["data"]["device_group_id"] == 224
    assert "Successfully created device group rule" in result["message"]
    
    # Verify API call
    mock_api_client.post.assert_called_once()
    call_args = mock_api_client.post.call_args
    assert call_args[0][0] == "/api/v3/devicegroups/rules"
    assert call_args[1]["json_data"]["groupId"] == "224"
    assert call_args[1]["json_data"]["namespaceId"] == "14"
    assert call_args[1]["json_data"]["attributeId"] == "185"
    assert call_args[1]["json_data"]["metadataValueExpression"] == "WiFi Access Point"


@pytest.mark.asyncio
async def test_add_name_expression_rule(mock_api_client, tool):
    """Test adding a name expression-based device group rule"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": "456",
        "groupId": "224",
        "nameExpression": "router.*"
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_group_id=224,
        name_expression="router.*"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["rule_id"] == 456
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["nameExpression"] == "router.*"


@pytest.mark.asyncio
async def test_add_multiple_criteria_rule(mock_api_client, tool):
    """Test adding a rule with multiple criteria"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": "789",
        "groupId": "224",
        "nameExpression": "switch.*",
        "sysLocationExpression": "Building A"
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_group_id=224,
        name_expression="switch.*",
        sys_location_expression="Building A"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["rule_id"] == 789
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["nameExpression"] == "switch.*"
    assert call_args[1]["json_data"]["sysLocationExpression"] == "Building A"


@pytest.mark.asyncio
async def test_missing_criteria(mock_api_client, tool):
    """Test error when no matching criteria provided"""
    result = await tool.execute(
        mock_api_client,
        device_group_id=224
    )
    
    # Verify error
    assert result["success"] is False
    assert "at least one matching criterion" in result["error"].lower()


@pytest.mark.asyncio
async def test_incomplete_metadata_rule(mock_api_client, tool):
    """Test error when metadata rule is incomplete"""
    result = await tool.execute(
        mock_api_client,
        device_group_id=224,
        namespace_id=14,
        # Missing attribute_id and metadata_value_expression
    )
    
    # Verify error
    assert result["success"] is False
    assert "at least one matching criterion" in result["error"].lower()


@pytest.mark.asyncio
async def test_api_error(mock_api_client, tool):
    """Test handling of API errors"""
    # Mock API error
    mock_api_client.post.side_effect = Exception("API connection failed")
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_group_id=224,
        name_expression="test.*"
    )
    
    # Verify error handling
    assert result["success"] is False
    assert "API connection failed" in result["error"]


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "add_devicegroup_rules"
    assert "device group rules" in tool.description.lower()
    assert "device_group_id" in tool.input_schema["properties"]
    assert "namespace_id" in tool.input_schema["properties"]
    assert "name_expression" in tool.input_schema["properties"]
    assert tool.input_schema["required"] == ["device_group_id"]


# Made with Bob