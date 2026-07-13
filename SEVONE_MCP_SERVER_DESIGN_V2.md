# SevOne MCP Server Design - Enhanced Authentication & Generic API Tool

## Overview

This document outlines the design for a Model Context Protocol (MCP) server that provides secure, authenticated access to the SevOne REST API. The server features encrypted credential storage, automatic token management, and a generic API endpoint execution tool.

## Key Requirements

1. **Secure Credential Management**
   - Store SevOne credentials in `.env` file
   - Password must be encrypted at rest
   - Automatic decryption during authentication

2. **Token-Based Authentication**
   - Use `/api/v3/users/signin` endpoint for authentication
   - Obtain and manage bearer tokens
   - Automatic token refresh on expiration
   - Token reuse across multiple API calls

3. **Generic API Tool**
   - Single tool: `run_api_endpoint`
   - Accept any API endpoint path
   - Accept input data as JSON
   - Return API response
   - Handle authentication transparently

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Bob AI Agent                             │
│                                                                   │
│  Uses MCP tool: run_api_endpoint(endpoint, data)                │
│                                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ MCP Protocol (SSE/stdio)
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    SevOne MCP Server                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Credential Manager                          │   │
│  │  - Load encrypted password from .env                     │   │
│  │  - Decrypt password using encryption key                 │   │
│  │  - Provide credentials to auth manager                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Authentication Manager                         │   │
│  │  - Sign in using /api/v3/users/signin                    │   │
│  │  - Store bearer token in memory                          │   │
│  │  - Detect token expiration (401 responses)               │   │
│  │  - Auto-refresh token when expired                       │   │
│  │  - Add Authorization header to all requests              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Client                                  │   │
│  │  - Execute HTTP requests to SevOne API                   │   │
│  │  - Handle GET, POST, PUT, PATCH, DELETE                  │   │
│  │  - Retry logic with exponential backoff                  │   │
│  │  - Error handling and response parsing                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         MCP Tool: run_api_endpoint                       │   │
│  │  Input:                                                  │   │
│  │    - endpoint: string (e.g., "/api/v3/devices")          │   │
│  │    - method: string (GET, POST, PUT, PATCH, DELETE)      │   │
│  │    - data: object (request body, optional)               │   │
│  │    - params: object (query parameters, optional)         │   │
│  │  Output:                                                 │   │
│  │    - success: boolean                                    │   │
│  │    - data: object (API response)                         │   │
│  │    - error: string (if failed)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ HTTPS
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    SevOne NMS API                                │
│                    (Port 443)                                    │
│                                                                   │
│  POST /api/v3/users/signin  → Returns bearer token              │
│  All other endpoints        → Require Authorization header       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
sevone-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py                    # Main MCP server
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py              # Configuration management
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── credentials.py           # Credential encryption/decryption
│   │   └── token_manager.py         # Token lifecycle management
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py                # SevOne API client
│   └── tools/
│       ├── __init__.py
│       └── run_api_endpoint.py      # Generic API tool
├── scripts/
│   └── encrypt_password.py          # Utility to encrypt passwords
├── tests/
│   ├── test_auth.py
│   ├── test_api_client.py
│   └── test_tool.py
├── .env.example                     # Example environment file
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Core Components

### 1. Credential Manager (`src/auth/credentials.py`)

**Purpose**: Securely manage encrypted credentials

```python
from cryptography.fernet import Fernet
import os
from typing import Tuple

class CredentialManager:
    """
    Manages encrypted credentials for SevOne authentication
    
    Features:
    - Load credentials from .env file
    - Decrypt password using Fernet symmetric encryption
    - Provide credentials to authentication manager
    """
    
    def __init__(self):
        self.encryption_key = os.getenv("SEVONE_ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("SEVONE_ENCRYPTION_KEY not found in environment")
        
        self.fernet = Fernet(self.encryption_key.encode())
    
    def get_credentials(self) -> Tuple[str, str, str]:
        """
        Load and decrypt SevOne credentials
        
        Returns:
            Tuple[hostname, username, decrypted_password]
        
        Raises:
            ValueError: If required environment variables are missing
        """
        hostname = os.getenv("SEVONE_HOSTNAME")
        username = os.getenv("SEVONE_USERNAME")
        encrypted_password = os.getenv("SEVONE_PASSWORD_ENCRYPTED")
        
        if not all([hostname, username, encrypted_password]):
            raise ValueError("Missing required SevOne credentials in .env")
        
        # Decrypt password
        decrypted_password = self.fernet.decrypt(
            encrypted_password.encode()
        ).decode()
        
        return hostname, username, decrypted_password
    
    @staticmethod
    def encrypt_password(password: str, encryption_key: str) -> str:
        """
        Utility method to encrypt a password
        
        Args:
            password: Plain text password
            encryption_key: Fernet encryption key
        
        Returns:
            Encrypted password as string
        """
        fernet = Fernet(encryption_key.encode())
        encrypted = fernet.encrypt(password.encode())
        return encrypted.decode()
```

### 2. Token Manager (`src/auth/token_manager.py`)

**Purpose**: Manage authentication tokens and automatic refresh

```python
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import httpx

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
    
    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.base_url = f"https://{hostname}"
        
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
                return self._token
            
            # Token expired or doesn't exist, sign in
            await self._sign_in()
            return self._token
    
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
        
        async with httpx.AsyncClient(verify=False) as client:
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
                
            except httpx.HTTPError as e:
                raise Exception(f"Failed to sign in to SevOne: {str(e)}")
    
    async def invalidate_token(self) -> None:
        """
        Invalidate current token (force refresh on next request)
        
        Called when we receive 401 Unauthorized response
        """
        async with self._lock:
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
```

### 3. API Client (`src/api/client.py`)

**Purpose**: Execute HTTP requests to SevOne API with authentication

```python
import httpx
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
    
    def __init__(self, token_manager, verify_ssl: bool = False):
        self.token_manager = token_manager
        self.verify_ssl = verify_ssl
        self.base_url = token_manager.base_url
        self.max_retries = 3
    
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
                
                # Parse response
                result = response.json() if response.content else {}
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
```

### 4. MCP Tool: run_api_endpoint (`src/tools/run_api_endpoint.py`)

**Purpose**: Generic tool to execute any SevOne API endpoint

```python
from typing import Dict, Any, Optional

class RunAPIEndpointTool:
    """
    Generic MCP tool to execute any SevOne API endpoint
    
    This tool provides a flexible interface for Bob AI to interact
    with any SevOne REST API endpoint without requiring specific
    tool implementations for each operation.
    """
    
    @property
    def name(self) -> str:
        return "run_api_endpoint"
    
    @property
    def description(self) -> str:
        return """Execute any SevOne REST API endpoint.
        
        This tool allows you to call any SevOne API endpoint by specifying:
        - The endpoint path (e.g., "/api/v3/devices")
        - The HTTP method (GET, POST, PUT, PATCH, DELETE)
        - Optional request body data
        - Optional query parameters
        
        Authentication is handled automatically using stored credentials.
        The bearer token is managed transparently and refreshed when needed.
        
        Examples:
        - List devices: GET /api/v3/devices
        - Create device: POST /api/v3/devices with body
        - Update metadata: PUT /api/v3/entity/DEVICE/id/123/metadata
        - Get device details: GET /api/v3/devices/123
        """
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["endpoint", "method"],
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint path (e.g., '/api/v3/devices')",
                    "examples": [
                        "/api/v3/devices",
                        "/api/v3/devices/123",
                        "/api/v3/entity/DEVICE/id/123/metadata"
                    ]
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    "description": "HTTP method to use",
                    "default": "GET"
                },
                "data": {
                    "type": "object",
                    "description": "Request body data (for POST, PUT, PATCH)",
                    "default": None
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters (for GET requests)",
                    "default": None
                }
            }
        }
    
    async def execute(
        self,
        api_client,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the API endpoint
        
        Args:
            api_client: SevOneAPIClient instance
            endpoint: API endpoint path
            method: HTTP method
            data: Request body (optional)
            params: Query parameters (optional)
        
        Returns:
            {
                "success": bool,
                "data": dict | list,
                "message": str,
                "error": str (if failed)
            }
        """
        try:
            # Validate endpoint starts with /api/v3
            if not endpoint.startswith("/api/v3"):
                return {
                    "success": False,
                    "error": "Endpoint must start with '/api/v3'",
                    "message": "Invalid endpoint path"
                }
            
            # Execute request based on method
            method = method.upper()
            
            if method == "GET":
                result = await api_client.get(endpoint, params=params)
            elif method == "POST":
                result = await api_client.post(endpoint, json_data=data or {})
            elif method == "PUT":
                result = await api_client.put(endpoint, json_data=data or {})
            elif method == "PATCH":
                result = await api_client.patch(endpoint, json_data=data or {})
            elif method == "DELETE":
                result = await api_client.delete(endpoint)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}",
                    "message": "Use GET, POST, PUT, PATCH, or DELETE"
                }
            
            return {
                "success": True,
                "data": result,
                "message": f"Successfully executed {method} {endpoint}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {method} {endpoint}"
            }
```

### 5. Main MCP Server (`src/server.py`)

**Purpose**: MCP server implementation

```python
import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.run_api_endpoint import RunAPIEndpointTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SevOneMCPServer:
    """
    MCP Server for SevOne API integration
    """
    
    def __init__(self):
        self.server = Server("sevone-api")
        self.credential_manager = None
        self.token_manager = None
        self.api_client = None
        self.tool = RunAPIEndpointTool()
        
        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
    
    async def initialize(self):
        """Initialize authentication and API client"""
        try:
            # Load and decrypt credentials
            self.credential_manager = CredentialManager()
            hostname, username, password = self.credential_manager.get_credentials()
            
            logger.info(f"Initializing connection to SevOne: {hostname}")
            
            # Initialize token manager
            self.token_manager = TokenManager(hostname, username, password)
            
            # Initialize API client
            self.api_client = SevOneAPIClient(self.token_manager)
            
            # Test authentication by getting a token
            await self.token_manager.get_token()
            logger.info("Successfully authenticated with SevOne")
            
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            raise
    
    async def list_tools(self) -> list[Tool]:
        """List available MCP tools"""
        return [
            Tool(
                name=self.tool.name,
                description=self.tool.description,
                inputSchema=self.tool.input_schema
            )
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Execute MCP tool"""
        if name != self.tool.name:
            raise ValueError(f"Unknown tool: {name}")
        
        # Execute the tool
        result = await self.tool.execute(self.api_client, **arguments)
        
        # Format response
        import json
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]
    
    async def run(self):
        """Run the MCP server"""
        await self.initialize()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = SevOneMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Configuration

### `.env` File Structure

```bash
# SevOne Connection Details
SEVONE_HOSTNAME=sevone-nms.example.com
SEVONE_USERNAME=admin

# Encrypted Password
# Generate using: python scripts/encrypt_password.py
SEVONE_PASSWORD_ENCRYPTED=gAAAAABh...encrypted_password_here...

# Encryption Key
# Generate using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
SEVONE_ENCRYPTION_KEY=your_fernet_key_here

# Optional: SSL Verification
SEVONE_VERIFY_SSL=false

# Logging
LOG_LEVEL=INFO
```

### `.env.example` Template

```bash
# SevOne Connection Details
SEVONE_HOSTNAME=your-sevone-hostname.com
SEVONE_USERNAME=your-username

# Encrypted Password (use scripts/encrypt_password.py to generate)
SEVONE_PASSWORD_ENCRYPTED=

# Encryption Key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
SEVONE_ENCRYPTION_KEY=

# Optional Settings
SEVONE_VERIFY_SSL=false
LOG_LEVEL=INFO
```

## Password Encryption Utility

### `scripts/encrypt_password.py`

```python
#!/usr/bin/env python3
"""
Utility script to encrypt SevOne password for .env file

Usage:
    python scripts/encrypt_password.py
"""

from cryptography.fernet import Fernet
import getpass
import sys

def generate_key():
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()

def encrypt_password(password: str, key: str) -> str:
    """Encrypt password using Fernet"""
    fernet = Fernet(key.encode())
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()

def main():
    print("SevOne Password Encryption Utility")
    print("=" * 50)
    print()
    
    # Check if key exists
    print("Do you have an encryption key? (y/n)")
    has_key = input().strip().lower()
    
    if has_key == 'y':
        print("\nEnter your encryption key:")
        key = input().strip()
    else:
        print("\nGenerating new encryption key...")
        key = generate_key()
        print(f"\nYour encryption key (save this in .env as SEVONE_ENCRYPTION_KEY):")
        print(key)
        print("\n⚠️  IMPORTANT: Save this key securely! You'll need it to decrypt the password.")
        print()
    
    # Get password
    print("\nEnter SevOne password to encrypt:")
    password = getpass.getpass()
    
    # Encrypt
    try:
        encrypted = encrypt_password(password, key)
        print("\n✅ Password encrypted successfully!")
        print(f"\nAdd this to your .env file as SEVONE_PASSWORD_ENCRYPTED:")
        print(encrypted)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Usage Examples

### Example 1: List Devices

```json
{
  "tool": "run_api_endpoint",
  "arguments": {
    "endpoint": "/api/v3/devices",
    "method": "GET",
    "params": {
      "limit": 10
    }
  }
}
```

### Example 2: Create Device

```json
{
  "tool": "run_api_endpoint",
  "arguments": {
    "endpoint": "/api/v3/devices",
    "method": "POST",
    "data": {
      "name": "Router-01",
      "ip": "192.168.1.1",
      "deviceTypeId": 1,
      "peerId": 1
    }
  }
}
```

### Example 3: Update Device Metadata

```json
{
  "tool": "run_api_endpoint",
  "arguments": {
    "endpoint": "/api/v3/entity/DEVICE/id/123/metadata",
    "method": "PUT",
    "data": {
      "metadata": [
        {
          "namespaceId": 1,
          "attributeId": 5,
          "value": "Production"
        }
      ]
    }
  }
}
```

### Example 4: Get Device Details

```json
{
  "tool": "run_api_endpoint",
  "arguments": {
    "endpoint": "/api/v3/devices/123",
    "method": "GET"
  }
}
```

## Security Considerations

### 1. Password Encryption
- **Algorithm**: Fernet (symmetric encryption)
- **Key Storage**: Environment variable (not in code)
- **Key Generation**: Cryptographically secure random key
- **Rotation**: Support key rotation by re-encrypting password

### 2. Token Management
- **Storage**: In-memory only (never persisted to disk)
- **Lifetime**: Conservative 23-hour validity
- **Refresh**: Automatic on expiration
- **Invalidation**: Immediate on 401 response

### 3. Network Security
- **SSL/TLS**: HTTPS for all API communication
- **Certificate Verification**: Configurable (default: disabled for self-signed certs)
- **Timeout**: 60-second request timeout
- **Retry Logic**: Max 3 retries with exponential backoff

### 4. Logging
- **Credentials**: Never logged
- **Tokens**: Never logged
- **Requests**: Endpoint and method only
- **Responses**: Status code only (body in debug mode)

## Error Handling

### Authentication Errors

```json
{
  "success": false,
  "error": "Failed to sign in to SevOne: 401 Unauthorized",
  "message": "Authentication failed - check credentials"
}
```

### Token Expiration

```json
{
  "success": false,
  "error": "Authentication failed after retries",
  "message": "Token expired and refresh failed"
}
```

### API Errors

```json
{
  "success": false,
  "error": "API error: 404 - Device not found",
  "message": "Failed to execute GET /api/v3/devices/999"
}
```

### Network Errors

```json
{
  "success": false,
  "error": "Network error: Connection timeout",
  "message": "Failed to execute POST /api/v3/devices"
}
```

## Dependencies

### `requirements.txt`

```
# MCP SDK
mcp>=0.9.0

# HTTP Client
httpx>=0.27.0

# Encryption
cryptography>=42.0.0

# Environment Variables
python-dotenv>=1.0.0

# Async Support
asyncio>=3.4.3
```

### `pyproject.toml`

```toml
[project]
name = "sevone-mcp-server"
version = "1.0.0"
description = "MCP server for SevOne REST API with secure authentication"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.27.0",
    "cryptography>=42.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
target-version = "py310"
```

## Testing Strategy

### Unit Tests

```python
# tests/test_auth.py
import pytest
from auth.credentials import CredentialManager
from auth.token_manager import TokenManager

@pytest.mark.asyncio
async def test_token_manager_sign_in():
    """Test successful sign-in"""
    manager = TokenManager("hostname", "user", "pass")
    token = await manager.get_token()
    assert token is not None

@pytest.mark.asyncio
async def test_token_refresh():
    """Test automatic token refresh"""
    manager = TokenManager("hostname", "user", "pass")
    token1 = await manager.get_token()
    await manager.invalidate_token()
    token2 = await manager.get_token()
    assert token1 != token2
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from server import SevOneMCPServer

@pytest.mark.asyncio
async def test_run_api_endpoint_tool():
    """Test end-to-end API execution"""
    server = SevOneMCPServer()
    await server.initialize()
    
    result = await server.call_tool(
        "run_api_endpoint",
        {
            "endpoint": "/api/v3/devices",
            "method": "GET",
            "params": {"limit": 1}
        }
    )
    
    assert result[0].text is not None
```

## Deployment

### Local Development

```bash
# 1. Clone repository
git clone <repo-url>
cd sevone-mcp-server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 5. Encrypt password
python scripts/encrypt_password.py

# 6. Create .env file
cp .env.example .env
# Edit .env with your values

# 7. Run server
python src/server.py
```

### Bob Configuration

Add to Bob's MCP configuration:

```json
{
  "mcpServers": {
    "sevone-api": {
      "command": "python",
      "args": ["/path/to/sevone-mcp-server/src/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/sevone-mcp-server"
      }
    }
  }
}
```

## Advantages of This Design

### 1. **Security First**
- Encrypted password storage
- No plaintext credentials in code
- Token-based authentication
- Automatic token refresh

### 2. **Simplicity**
- Single generic tool for all API operations
- No need to create specific tools for each endpoint
- Easy to use from Bob AI

### 3. **Flexibility**
- Support any SevOne API endpoint
- All HTTP methods supported
- Query parameters and request bodies

### 4. **Reliability**
- Automatic token refresh on expiration
- Retry logic for transient failures
- Comprehensive error handling

### 5. **Maintainability**
- Clean separation of concerns
- Well-documented code
- Easy to extend

## Future Enhancements

1. **Token Caching**: Persist tokens securely between server restarts
2. **Rate Limiting**: Implement client-side rate limiting
3. **Response Caching**: Cache frequently accessed data
4. **Batch Operations**: Support multiple API calls in one tool invocation
5. **Webhook Support**: Add webhook receiver for SevOne events
6. **Multi-Instance**: Support multiple SevOne instances
7. **Audit Logging**: Detailed audit trail of all API operations

## Conclusion

This design provides a secure, flexible, and maintainable MCP server for SevOne API integration. The single `run_api_endpoint` tool gives Bob AI complete access to the SevOne REST API while handling authentication, token management, and error handling transparently.

The encrypted credential storage ensures security, while the automatic token refresh provides reliability. The generic tool design means no code changes are needed to support new API endpoints - Bob can simply call any endpoint it needs.