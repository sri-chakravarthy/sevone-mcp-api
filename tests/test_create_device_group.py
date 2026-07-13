"""Tests for create_device_group tool"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import AsyncMock, MagicMock
from tools.create_device_group import CreateDeviceGroupTool


@pytest.fixture
def mock_api_client():
    """Create a mock API client"""
    client = MagicMock()
    client.post = AsyncMock()
    return client


@pytest.fixture
def tool():
    """Create tool instance"""
    return CreateDeviceGroupTool()


@pytest.mark.asyncio
async def test_create_root_level_group(mock_api_client, tool):
    """Test creating a device group at root level"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": 100,
        "name": "My New Group"
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="My New Group"
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["id"] == 100
    assert result["data"]["name"] == "My New Group"
    assert "created successfully" in result["message"]
    
    # Verify API call
    mock_api_client.post.assert_called_once()
    call_args = mock_api_client.post.call_args
    assert call_args[0][0] == "/api/v3/devicegroups"
    assert call_args[1]["data"]["name"] == "My New Group"
    assert "parentId" not in call_args[1]["data"]
    assert "parentPath" not in call_args[1]["data"]


@pytest.mark.asyncio
async def test_create_group_with_parent_id(mock_api_client, tool):
    """Test creating a device group with parent ID"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": 101,
        "name": "Child Group",
        "parentId": 10
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="Child Group",
        parent_id=10
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["id"] == 101
    assert result["data"]["name"] == "Child Group"
    assert result["data"]["parent_id"] == 10
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["data"]["name"] == "Child Group"
    assert call_args[1]["data"]["parentId"] == 10


@pytest.mark.asyncio
async def test_create_group_with_parent_path(mock_api_client, tool):
    """Test creating a device group with parent path"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": 102,
        "name": "Seattle Office",
        "parentPath": {
            "pathComponents": ["All Device Groups", "West Coast", "Washington"]
        }
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="Seattle Office",
        parent_path=["All Device Groups", "West Coast", "Washington"]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["id"] == 102
    assert result["data"]["name"] == "Seattle Office"
    assert result["data"]["parent_path"] == ["All Device Groups", "West Coast", "Washington"]
    
    # Verify API call
    call_args = mock_api_client.post.call_args
    assert call_args[1]["data"]["name"] == "Seattle Office"
    assert call_args[1]["data"]["parentPath"]["pathComponents"] == ["All Device Groups", "West Coast", "Washington"]


@pytest.mark.asyncio
async def test_parent_id_takes_precedence(mock_api_client, tool):
    """Test that parent_id takes precedence over parent_path"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": 103,
        "name": "Test Group",
        "parentId": 20
    }
    
    # Execute tool with both parent_id and parent_path
    result = await tool.execute(
        mock_api_client,
        name="Test Group",
        parent_id=20,
        parent_path=["All Device Groups", "Other"]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["parent_id"] == 20
    
    # Verify API call - should only have parentId, not parentPath
    call_args = mock_api_client.post.call_args
    assert call_args[1]["data"]["parentId"] == 20
    assert "parentPath" not in call_args[1]["data"]


@pytest.mark.asyncio
async def test_empty_name_error(mock_api_client, tool):
    """Test error when name is empty"""
    result = await tool.execute(
        mock_api_client,
        name=""
    )
    
    # Verify error
    assert result["success"] is False
    assert "cannot be empty" in result["error"]


@pytest.mark.asyncio
async def test_whitespace_name_error(mock_api_client, tool):
    """Test error when name is only whitespace"""
    result = await tool.execute(
        mock_api_client,
        name="   "
    )
    
    # Verify error
    assert result["success"] is False
    assert "cannot be empty" in result["error"]


@pytest.mark.asyncio
async def test_name_trimming(mock_api_client, tool):
    """Test that name is trimmed of whitespace"""
    # Mock API response
    mock_api_client.post.return_value = {
        "id": 104,
        "name": "Trimmed Group"
    }
    
    # Execute tool with whitespace in name
    result = await tool.execute(
        mock_api_client,
        name="  Trimmed Group  "
    )
    
    # Verify API call has trimmed name
    call_args = mock_api_client.post.call_args
    assert call_args[1]["data"]["name"] == "Trimmed Group"


@pytest.mark.asyncio
async def test_api_error(mock_api_client, tool):
    """Test handling of API errors"""
    # Mock API error
    mock_api_client.post.side_effect = Exception("API connection failed")
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        name="Test Group"
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
        name="Test Group"
    )
    
    # Verify error handling
    assert result["success"] is False
    assert "Unexpected response format" in result["error"]


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "create_device_group"
    assert "create" in tool.description.lower()
    assert "device group" in tool.description.lower()
    assert "name" in tool.input_schema["properties"]
    assert "parent_id" in tool.input_schema["properties"]
    assert "parent_path" in tool.input_schema["properties"]
    assert tool.input_schema["required"] == ["name"]


# Made with Bob