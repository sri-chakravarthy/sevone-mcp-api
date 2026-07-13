"""Tests for get_alerting_policy_details tool"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import AsyncMock, MagicMock
from tools.get_alerting_policy_details import GetAlertingPolicyDetailsTool


@pytest.fixture
def mock_api_client():
    """Create a mock API client"""
    client = MagicMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def tool():
    """Create tool instance"""
    return GetAlertingPolicyDetailsTool()


@pytest.mark.asyncio
async def test_get_policy_by_name(mock_api_client, tool):
    """Test getting policies by name"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 123,
                "name": "High CPU Alert",
                "description": "Alert when CPU exceeds threshold",
                "severity": "CRITICAL",
                "userEnabled": True,
                "isDeviceGroup": False,
                "type": "POLICY_TYPE_OTHER",
                "triggerExpression": "value > 90",
                "clearExpression": "value < 80",
                "lastUpdated": "2024-01-01T00:00:00Z",
                "folderId": 1,
                "objectTypeId": 10,
                "objectSubTypeId": 20
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="High CPU Alert"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert result["data"]["policies"][0]["id"] == 123
    assert result["data"]["policies"][0]["name"] == "High CPU Alert"
    assert result["data"]["policies"][0]["severity"] == "CRITICAL"
    
    # Verify API call
    mock_api_client.post.assert_called_once()
    call_args = mock_api_client.post.call_args
    assert call_args[0][0] == "/api/v3/policies/filter"
    assert call_args[1]["json_data"]["name"]["value"] == "High CPU Alert"
    assert call_args[1]["json_data"]["name"]["isFuzzy"] is True


@pytest.mark.asyncio
async def test_get_policies_by_severities(mock_api_client, tool):
    """Test getting policies by alert severities"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 456,
                "name": "Critical Alert",
                "severity": "CRITICAL",
                "userEnabled": True,
                "isDeviceGroup": False
            },
            {
                "id": 789,
                "name": "Error Alert",
                "severity": "ERROR",
                "userEnabled": True,
                "isDeviceGroup": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        alert_severities=["CRITICAL", "ERROR"]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 2
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["alertSeverities"] == ["CRITICAL", "ERROR"]


@pytest.mark.asyncio
async def test_get_policies_by_ids(mock_api_client, tool):
    """Test getting policies by policy IDs"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 123,
                "name": "Policy 1",
                "severity": "WARNING",
                "userEnabled": True,
                "isDeviceGroup": False
            },
            {
                "id": 456,
                "name": "Policy 2",
                "severity": "CRITICAL",
                "userEnabled": False,
                "isDeviceGroup": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        policy_ids=[123, 456]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 2
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["ids"] == [123, 456]


@pytest.mark.asyncio
async def test_get_policies_by_folder_ids(mock_api_client, tool):
    """Test getting policies by folder IDs"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 555,
                "name": "Folder Policy 1",
                "severity": "WARNING",
                "userEnabled": True,
                "isDeviceGroup": False,
                "folderId": 1
            },
            {
                "id": 666,
                "name": "Folder Policy 2",
                "severity": "ERROR",
                "userEnabled": True,
                "isDeviceGroup": False,
                "folderId": 2
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        folder_ids=[1, 2]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 2
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["folderIds"] == [1, 2]


@pytest.mark.asyncio
async def test_get_policies_by_device_group(mock_api_client, tool):
    """Test getting policies by device group ID"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 789,
                "name": "Group Policy",
                "severity": "ERROR",
                "userEnabled": True,
                "isDeviceGroup": True,
                "groupId": 10
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_group_id=10
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert result["data"]["policies"][0]["is_device_group"] is True
    assert result["data"]["policies"][0]["device_group_id"] == 10
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["groupId"] == 10


@pytest.mark.asyncio
async def test_get_enabled_policies(mock_api_client, tool):
    """Test getting enabled policies"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 111,
                "name": "Enabled Policy",
                "severity": "WARNING",
                "userEnabled": True,
                "isDeviceGroup": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        is_enabled=True
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["policies"][0]["is_enabled"] is True
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["isEnabled"] == "MATCH_TRUE"


@pytest.mark.asyncio
async def test_get_disabled_policies(mock_api_client, tool):
    """Test getting disabled policies"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 222,
                "name": "Disabled Policy",
                "severity": "ERROR",
                "userEnabled": False,
                "isDeviceGroup": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        is_enabled=False
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["policies"][0]["is_enabled"] is False
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["isEnabled"] == "MATCH_FALSE"


@pytest.mark.asyncio
async def test_combined_filters(mock_api_client, tool):
    """Test combining multiple filters"""
    # Mock API response
    mock_api_client.post.return_value = {
        "policies": [
            {
                "id": 333,
                "name": "Combined Filter Policy",
                "severity": "CRITICAL",
                "userEnabled": True,
                "isDeviceGroup": True,
                "groupId": 10,
                "folderId": 1
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        alert_severities=["CRITICAL"],
        is_enabled=True,
        device_group_id=10,
        folder_ids=[1]
    )
    
    # Verify result
    assert result["success"] is True
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["alertSeverities"] == ["CRITICAL"]
    assert call_args[1]["json_data"]["isEnabled"] == "MATCH_TRUE"
    assert call_args[1]["json_data"]["groupId"] == 10
    assert call_args[1]["json_data"]["folderIds"] == [1]


@pytest.mark.asyncio
async def test_missing_filters(mock_api_client, tool):
    """Test error when no filters provided"""
    result = await tool.execute(mock_api_client)
    
    # Verify error
    assert result["success"] is False
    assert "at least one filter criterion" in result["error"].lower()


@pytest.mark.asyncio
async def test_invalid_severity(mock_api_client, tool):
    """Test error with invalid severity"""
    result = await tool.execute(
        mock_api_client,
        alert_severities=["INVALID", "CRITICAL"]
    )
    
    # Verify error
    assert result["success"] is False
    assert "invalid alert severities" in result["error"].lower()


@pytest.mark.asyncio
async def test_invalid_page_size(mock_api_client, tool):
    """Test error with invalid page size"""
    result = await tool.execute(
        mock_api_client,
        name="Test",
        page_size=2000
    )
    
    # Verify error
    assert result["success"] is False
    assert "page_size must be between" in result["error"].lower()


@pytest.mark.asyncio
async def test_api_error(mock_api_client, tool):
    """Test handling of API errors"""
    # Mock API error
    mock_api_client.post.side_effect = Exception("API connection failed")
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="Test Policy"
    )
    
    # Verify error handling
    assert result["success"] is False
    assert "API connection failed" in result["error"]


@pytest.mark.asyncio
async def test_unexpected_response_format(mock_api_client, tool):
    """Test handling of unexpected response format"""
    # Mock unexpected response
    mock_api_client.post.return_value = None
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="Test Policy"
    )
    
    # Verify error handling
    assert result["success"] is False
    assert "Unexpected response format" in result["error"]


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "get_alerting_policy_details"
    assert "alerting policy" in tool.description.lower()
    assert "name" in tool.input_schema["properties"]
    assert "alert_severities" in tool.input_schema["properties"]
    assert "policy_ids" in tool.input_schema["properties"]
    assert "folder_ids" in tool.input_schema["properties"]
    assert "device_group_id" in tool.input_schema["properties"]
    assert "is_enabled" in tool.input_schema["properties"]


# Made with Bob