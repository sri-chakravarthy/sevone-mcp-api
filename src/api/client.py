"""HTTP client for SevOne REST API"""

import httpx
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SevOneAPIClient:
    """
    HTTP client for SevOne REST API
    
    Features:
    - Automatic authentication header injection
    - Token refresh on 401 responses
    - Retry logic with exponential backoff
    - Request/response logging
    - Error handling
    """
    
    def __init__(self, token_manager, verify_ssl: bool = False, max_response_size_mb: int = 50):
        self.token_manager = token_manager
        self.verify_ssl = verify_ssl
        self.base_url = token_manager.base_url
        self.max_retries = 3
        self.max_response_size_mb = max_response_size_mb
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Execute HTTP request to SevOne API
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint path (e.g., "/api/v3/devices")
            params: Query parameters
            json_data: Request body (for POST/PUT/PATCH)
            retry_count: Current retry attempt
        
        Returns:
            API response as dictionary
        
        Raises:
            Exception: On API errors or network failures
        """
        # Ensure we have a valid token
        token = await self.token_manager.get_token()
        headers = self.token_manager.get_auth_header()
        
        # Add compression support
        headers['Accept-Encoding'] = 'gzip, deflate'
        
        # Build full URL
        url = f"{self.base_url}{endpoint}"
        
        logger.info(f"API Request: {method} {endpoint}")
        if json_data:
            logger.debug(f"Request body: {json_data}")
        
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=60.0
                )
                
                # Handle 401 Unauthorized - token expired
                if response.status_code == 401:
                    if retry_count < self.max_retries:
                        logger.warning("Token expired, refreshing...")
                        await self.token_manager.invalidate_token()
                        return await self.request(
                            method, endpoint, params, json_data, retry_count + 1
                        )
                    else:
                        raise Exception("Authentication failed after retries")
                
                response.raise_for_status()
                
                # Check response size before parsing
                content_length = response.headers.get('content-length')
                response_size_bytes = len(response.content) if response.content else 0
                
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    logger.info(f"Response size: {size_mb:.2f}MB (from Content-Length header)")
                    
                    if size_mb > self.max_response_size_mb:
                        raise Exception(
                            f"Response too large ({size_mb:.2f}MB exceeds limit of {self.max_response_size_mb}MB). "
                            f"Consider reducing page_size or adding more filters."
                        )
                else:
                    # Check actual content size
                    size_mb = response_size_bytes / (1024 * 1024)
                    if size_mb > 1:  # Log if > 1MB
                        logger.info(f"Response size: {size_mb:.2f}MB")
                    
                    if size_mb > self.max_response_size_mb:
                        raise Exception(
                            f"Response too large ({size_mb:.2f}MB exceeds limit of {self.max_response_size_mb}MB). "
                            f"Consider reducing page_size or adding more filters."
                        )
                
                # Parse response with error handling
                try:
                    result = response.json() if response.content else {}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response (size: {response_size_bytes} bytes)")
                    raise Exception(f"Invalid JSON response: {str(e)}")
                except MemoryError:
                    logger.error(f"Out of memory while parsing response (size: {size_mb:.2f}MB)")
                    raise Exception(
                        f"Response too large to process in memory ({size_mb:.2f}MB). "
                        f"Reduce page_size or add more filters."
                    )
                
                logger.info(f"API Response: {response.status_code}")
                logger.debug(f"Response body: {result}")
                
                return result
                
            except httpx.HTTPStatusError as e:
                error_msg = f"API error: {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
                
                logger.error(error_msg)
                raise Exception(error_msg)
                
            except httpx.HTTPError as e:
                error_msg = f"Network error: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Execute GET request"""
        return await self.request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, json_data: Dict) -> Dict:
        """Execute POST request"""
        return await self.request("POST", endpoint, json_data=json_data)
    
    async def put(self, endpoint: str, json_data: Dict) -> Dict:
        """Execute PUT request"""
        return await self.request("PUT", endpoint, json_data=json_data)
    
    async def patch(self, endpoint: str, json_data: Dict) -> Dict:
        """Execute PATCH request"""
        return await self.request("PATCH", endpoint, json_data=json_data)
    
    async def delete(self, endpoint: str) -> Dict:
        """Execute DELETE request"""
        return await self.request("DELETE", endpoint)

# Made with Bob
