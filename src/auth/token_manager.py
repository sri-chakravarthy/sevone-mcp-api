"""Token management for SevOne API authentication"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages SevOne API authentication tokens
    
    Features:
    - Sign in to obtain bearer token
    - Store token in memory
    - Detect token expiration
    - Automatic token refresh
    - Thread-safe token access
    """
    
    def __init__(self, hostname: str, username: str, password: str, verify_ssl: bool = False):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.base_url = f"https://{hostname}"
        self.verify_ssl = verify_ssl
        
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()
        
        # Token validity duration (conservative estimate)
        # SevOne tokens typically last 24 hours, we'll refresh at 23 hours
        self.token_lifetime = timedelta(hours=23)
    
    async def get_token(self) -> str:
        """
        Get valid authentication token
        
        Returns:
            Valid bearer token
        
        Automatically refreshes if expired
        """
        async with self._lock:
            if self._is_token_valid():
                return self._token  # type: ignore
            
            # Token expired or doesn't exist, sign in
            await self._sign_in()
            return self._token  # type: ignore
    
    def _is_token_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._token or not self._token_expiry:
            return False
        
        # Add 5-minute buffer before expiry
        return datetime.now() < (self._token_expiry - timedelta(minutes=5))
    
    async def _sign_in(self) -> None:
        """
        Sign in to SevOne and obtain bearer token
        
        Uses: POST /api/v3/users/signin
        Request: {"username": "...", "password": "..."}
        Response: {"token": "...", "user": {...}}
        """
        signin_url = f"{self.base_url}/api/v3/users/signin"
        
        logger.info(f"Signing in to SevOne at {self.hostname}")
        
        async with httpx.AsyncClient(verify=self.verify_ssl) as client:
            try:
                response = await client.post(
                    signin_url,
                    json={
                        "username": self.username,
                        "password": self.password
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                self._token = data.get("token")
                
                if not self._token:
                    raise ValueError("No token in sign-in response")
                
                # Set expiry time
                self._token_expiry = datetime.now() + self.token_lifetime
                
                logger.info("Successfully obtained authentication token")
                
            except httpx.HTTPStatusError as e:
                error_msg = f"Failed to sign in: HTTP {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except httpx.HTTPError as e:
                error_msg = f"Failed to sign in to SevOne: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
    
    async def invalidate_token(self) -> None:
        """
        Invalidate current token (force refresh on next request)
        
        Called when we receive 401 Unauthorized response
        """
        async with self._lock:
            logger.warning("Token invalidated, will refresh on next request")
            self._token = None
            self._token_expiry = None
    
    def get_auth_header(self) -> dict:
        """
        Get Authorization header for API requests
        
        Returns:
            Dictionary with Authorization header
        """
        if not self._token:
            raise ValueError("No valid token available")
        
        return {"Authorization": f"Bearer {self._token}"}

# Made with Bob
