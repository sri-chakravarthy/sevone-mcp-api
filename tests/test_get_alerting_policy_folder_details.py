"""Tests for get_alerting_policy_folder_details tool"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from tools.get_alerting_policy_folder_details import GetAlertingPolicyFolderDetailsTool


@pytest.fixture
def tool():
    """Create tool instance"""
    return GetAlertingPolicyFolderDetailsTool()


@pytest.fixture
def mock_api_client():
    """Create mock API client"""
    client = MagicMock()
    client.get = AsyncMock()
    return client


def test_tool_properties(tool):
    """Test tool properties"""
    assert tool.name == "get_alerting_policy_folder_details"
    assert "policy folder" in tool.description.lower()
    assert tool.input_schema["type"] == "object"


@pytest.mark.asyncio
async def test_get_all_folders_success(tool, mock_api_client):
    """Test successful retrieval of all folders"""
    # Mock API response
    mock_api_client.get.return_value = {
        "policyFolders": [
            {
                "id": "1",
                "name": "Default Policies",
                "parentId": "0",
                "isEditable": True
            },
            {
                "id": "2",
                "name": "Network Policies",
                "parentId": "1",
                "isEditable": True
            },
            {
                "id": "3",
                "name": "System Policies",
                "parentId": "0",
                "isEditable": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(mock_api_client)
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 3
    assert len(result["data"]["folders"]) == 3
    
    # Verify first folder
    folder1 = result["data"]["folders"][0]
    assert folder1["id"] == "1"
    assert folder1["name"] == "Default Policies"
    assert folder1["parent_id"] == "0"
    assert folder1["is_editable"] is True
    
    # Verify API call
    mock_api_client.get.assert_called_once()
    call_args = mock_api_client.get.call_args
    assert call_args[0][0] == "/api/v3/policies/folders"
    assert call_args[1]["params"]["pagination.limit"] == "100"


@pytest.mark.asyncio
async def test_get_folders_with_custom_page_size(tool, mock_api_client):
    """Test retrieval with custom page size"""
    # Mock API response
    mock_api_client.get.return_value = {
        "policyFolders": [
            {
                "id": "1",
                "name": "Test Folder",
                "parentId": "0",
                "isEditable": True
            }
        ]
    }
    
    # Execute tool with custom page size
    result = await tool.execute(mock_api_client, page_size=50)
    
    # Verify result
    assert result["success"] is True
    
    # Verify API call with custom page size
    call_args = mock_api_client.get.call_args
    assert call_args[1]["params"]["pagination.limit"] == "50"


@pytest.mark.asyncio
async def test_invalid_page_size_too_small(tool, mock_api_client):
    """Test with page_size less than 1"""
    result = await tool.execute(mock_api_client, page_size=0)
    
    assert result["success"] is False
    assert "page_size must be between 1 and 1000" in result["error"]
    mock_api_client.get.assert_not_called()


@pytest.mark.asyncio
async def test_invalid_page_size_too_large(tool, mock_api_client):
    """Test with page_size greater than 1000"""
    result = await tool.execute(mock_api_client, page_size=1001)
    
    assert result["success"] is False
    assert "page_size must be between 1 and 1000" in result["error"]
    mock_api_client.get.assert_not_called()


@pytest.mark.asyncio
async def test_empty_folders_response(tool, mock_api_client):
    """Test with empty folders list"""
    # Mock API response with no folders
    mock_api_client.get.return_value = {
        "policyFolders": []
    }
    
    # Execute tool
    result = await tool.execute(mock_api_client)
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 0
    assert len(result["data"]["folders"]) == 0


@pytest.mark.asyncio
async def test_api_error(tool, mock_api_client):
    """Test handling of API errors"""
    # Mock API error
    mock_api_client.get.side_effect = Exception("API connection failed")
    
    # Execute tool
    result = await tool.execute(mock_api_client)
    
    # Verify error handling
    assert result["success"] is False
    assert "API connection failed" in result["error"]
    assert "Failed to retrieve alerting policy folders" in result["message"]


@pytest.mark.asyncio
async def test_unexpected_response_format(tool, mock_api_client):
    """Test handling of unexpected response format"""
    # Mock unexpected response (missing policyFolders key)
    mock_api_client.get.return_value = {"unexpected": "format"}
    
    # Execute tool
    result = await tool.execute(mock_api_client)
    
    # Verify it treats missing data as empty list (graceful degradation)
    assert result["success"] is True
    assert result["data"]["total_count"] == 0
    assert len(result["data"]["folders"]) == 0


@pytest.mark.asyncio
async def test_folder_with_all_fields(tool, mock_api_client):
    """Test folder with all fields populated"""
    # Mock API response
    mock_api_client.get.return_value = {
        "policyFolders": [
            {
                "id": "42",
                "name": "Custom Folder",
                "parentId": "10",
                "isEditable": False
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(mock_api_client)
    
    # Verify all fields are present
    folder = result["data"]["folders"][0]
    assert folder["id"] == "42"
    assert folder["name"] == "Custom Folder"
    assert folder["parent_id"] == "10"
    assert folder["is_editable"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob