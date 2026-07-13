"""Tests for get_indicator_details tool"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from tools.get_indicator_details import GetIndicatorDetailsTool


@pytest.fixture
def mock_api_client():
    """Create a mock API client"""
    client = AsyncMock()
    return client


@pytest.fixture
def tool():
    """Create tool instance"""
    return GetIndicatorDetailsTool()


@pytest.mark.asyncio
async def test_get_indicators_by_device_ids(mock_api_client, tool):
    """Test getting indicators by device IDs"""
    # Mock API response
    mock_api_client.post.return_value = {
        "indicators": [
            {
                "id": "1",
                "indicatorTypeId": "5",
                "indicatorTypeName": "CPU Usage",
                "deviceId": "123",
                "objectId": "456"
            }
        ]
    }
    
    # Execute tool
    result = await tool.execute(
        mock_api_client,
        device_ids=[123]
    )
    
    # Verify result
    assert result["success"] is True
    assert result["data"]["total_count"] == 1
    assert len(result["data"]["indicators"]) == 1
    
    # Verify API was called correctly
    mock_api_client.post.assert_called_once()
    call_args = mock_api_client.post.call_args
    assert call_args[0][0] == "/api/v3/metadata/indicators"
    assert "filters" in call_args[1]["json_data"]


@pytest.mark.asyncio
async def test_get_indicators_by_device_names(mock_api_client, tool):
    """Test getting indicators by device names"""
    mock_api_client.post.return_value = {
        "indicators": [
            {"id": "1", "indicatorTypeName": "Memory Usage"}
        ]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_names=["router1", "switch2"]
    )
    
    assert result["success"] is True
    assert result["data"]["total_count"] == 1


@pytest.mark.asyncio
async def test_get_indicators_by_device_object_pairs(mock_api_client, tool):
    """Test getting indicators by device-object pairs"""
    mock_api_client.post.return_value = {
        "indicators": [
            {"id": "1", "deviceId": "123", "objectId": "456"}
        ]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_object_pairs=[["router1", "eth0"], ["switch2", "port1"]]
    )
    
    assert result["success"] is True
    assert result["data"]["total_count"] == 1


@pytest.mark.asyncio
async def test_get_indicators_by_indicator_ids(mock_api_client, tool):
    """Test getting indicators by indicator IDs"""
    mock_api_client.post.return_value = {
        "indicators": [
            {"id": "789", "indicatorTypeName": "Bandwidth"}
        ]
    }
    
    result = await tool.execute(
        mock_api_client,
        indicator_ids=[789, 101112]
    )
    
    assert result["success"] is True
    assert result["data"]["total_count"] == 1


@pytest.mark.asyncio
async def test_get_indicators_with_fuzzy_match(mock_api_client, tool):
    """Test getting indicators with fuzzy matching"""
    mock_api_client.post.return_value = {
        "indicators": [
            {"id": "1", "indicatorTypeName": "CPU"}
        ]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_names=["router*"],
        fuzzy_match=True
    )
    
    assert result["success"] is True
    
    # Verify fuzzy match was used
    call_args = mock_api_client.post.call_args
    filters = call_args[1]["json_data"]["filters"][0]
    assert filters["deviceNames"][0]["type"] == "FUZZABLE_STRING_TYPE_FUZZY"


@pytest.mark.asyncio
async def test_get_indicators_with_metadata_filter(mock_api_client, tool):
    """Test getting indicators with device metadata filter"""
    mock_api_client.post.return_value = {
        "indicators": [
            {"id": "1", "indicatorTypeName": "Temperature"}
        ]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_metadata_namespace="System",
        device_metadata_attribute="Location",
        device_metadata_value="Building A"
    )
    
    assert result["success"] is True


@pytest.mark.asyncio
async def test_get_indicators_truncation(mock_api_client, tool):
    """Test that large result sets are truncated"""
    # Create 150 indicators
    indicators = [{"id": str(i)} for i in range(150)]
    mock_api_client.post.return_value = {
        "indicators": indicators
    }
    
    result = await tool.execute(
        mock_api_client,
        device_ids=[123]
    )
    
    assert result["success"] is True
    assert result["data"]["total_count"] == 150
    assert len(result["data"]["indicators"]) == 100  # Truncated to 100
    assert result["data"]["truncated"] is True
    assert "truncated_message" in result["data"]


@pytest.mark.asyncio
async def test_missing_required_parameters(mock_api_client, tool):
    """Test error when no filter is provided"""
    result = await tool.execute(mock_api_client)
    
    assert result["success"] is False
    assert "at least one filter" in result["error"].lower()


@pytest.mark.asyncio
async def test_incomplete_metadata_parameters(mock_api_client, tool):
    """Test error when metadata parameters are incomplete"""
    result = await tool.execute(
        mock_api_client,
        device_metadata_namespace="System",
        device_metadata_attribute="Location"
        # Missing device_metadata_value
    )
    
    assert result["success"] is False
    assert "metadata parameters" in result["error"].lower()


@pytest.mark.asyncio
async def test_api_error_handling(mock_api_client, tool):
    """Test handling of API errors"""
    mock_api_client.post.side_effect = Exception("API connection failed")
    
    result = await tool.execute(
        mock_api_client,
        device_ids=[123]
    )
    
    assert result["success"] is False
    assert "API connection failed" in result["error"]


@pytest.mark.asyncio
async def test_custom_page_size(mock_api_client, tool):
    """Test custom page size parameter"""
    mock_api_client.post.return_value = {
        "indicators": [{"id": "1"}]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_ids=[123],
        page_size=50
    )
    
    assert result["success"] is True
    
    # Verify page size was used
    call_args = mock_api_client.post.call_args
    assert call_args[1]["json_data"]["pagination"]["limit"] == "50"


@pytest.mark.asyncio
async def test_multiple_filters_combined(mock_api_client, tool):
    """Test combining multiple filter types"""
    mock_api_client.post.return_value = {
        "indicators": [{"id": "1"}]
    }
    
    result = await tool.execute(
        mock_api_client,
        device_ids=[123],
        indicator_type_names=["CPU Usage"],
        object_ids=[456]
    )
    
    assert result["success"] is True
    
    # Verify all filters were included
    call_args = mock_api_client.post.call_args
    filters = call_args[1]["json_data"]["filters"][0]
    assert "deviceIds" in filters
    assert "indicatorTypeNames" in filters
    assert "objectIds" in filters


# Made with Bob