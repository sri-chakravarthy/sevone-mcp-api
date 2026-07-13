"""MCP server with SSE (Server-Sent Events) transport for remote access"""

import asyncio
import logging
import os
import argparse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.run_api_endpoint import RunAPIEndpointTool
from tools.get_device_details import GetDeviceDetailsTool
from tools.get_device_group_details import GetDeviceGroupDetailsTool
from tools.get_indicator_details import GetIndicatorDetailsTool

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SevOneMCPServerSSE:
    """
    MCP Server for SevOne API integration with SSE transport
    
    Provides secure, authenticated access to SevOne REST API
    through a generic run_api_endpoint tool over HTTP/SSE.
    """
    
    def __init__(self):
        self.server = Server("sevone-api")
        self.credential_manager = None
        self.token_manager = None
        self.api_client = None
        self.run_api_tool = RunAPIEndpointTool()
        self.get_device_details_tool = GetDeviceDetailsTool()
        self.get_device_group_details_tool = GetDeviceGroupDetailsTool()
        self.get_indicator_details_tool = GetIndicatorDetailsTool()
        
        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
    
    async def initialize(self):
        """Initialize authentication and API client"""
        try:
            logger.info("Initializing SevOne MCP Server (SSE)...")
            
            # Load and decrypt credentials
            self.credential_manager = CredentialManager()
            hostname, username, password = self.credential_manager.get_credentials()
            
            logger.info(f"Connecting to SevOne: {hostname}")
            
            # Get SSL verification setting
            verify_ssl = os.getenv("SEVONE_VERIFY_SSL", "false").lower() == "true"
            
            # Initialize token manager
            self.token_manager = TokenManager(
                hostname, 
                username, 
                password,
                verify_ssl=verify_ssl
            )
            
            # Initialize API client
            self.api_client = SevOneAPIClient(
                self.token_manager,
                verify_ssl=verify_ssl
            )
            
            # Test authentication by getting a token
            await self.token_manager.get_token()
            logger.info("✓ Successfully authenticated with SevOne")
            logger.info("✓ SevOne MCP Server ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize: {str(e)}")
            raise
    
    async def list_tools(self) -> list[Tool]:
        """List available MCP tools"""
        return [
            Tool(
                name=self.run_api_tool.name,
                description=self.run_api_tool.description,
                inputSchema=self.run_api_tool.input_schema
            ),
            Tool(
                name=self.get_device_details_tool.name,
                description=self.get_device_details_tool.description,
                inputSchema=self.get_device_details_tool.input_schema
            ),
            Tool(
                name=self.get_device_group_details_tool.name,
                description=self.get_device_group_details_tool.description,
                inputSchema=self.get_device_group_details_tool.input_schema
            ),
            Tool(
                name=self.get_indicator_details_tool.name,
                description=self.get_indicator_details_tool.description,
                inputSchema=self.get_indicator_details_tool.input_schema
            )
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Execute MCP tool"""
        logger.info(f"Executing tool: {name}")
        
        # Route to appropriate tool
        if name == self.run_api_tool.name:
            result = await self.run_api_tool.execute(self.api_client, **arguments)
        elif name == self.get_device_details_tool.name:
            result = await self.get_device_details_tool.execute(self.api_client, **arguments)
        elif name == self.get_device_group_details_tool.name:
            result = await self.get_device_group_details_tool.execute(self.api_client, **arguments)
        elif name == self.get_indicator_details_tool.name:
            result = await self.get_indicator_details_tool.execute(self.api_client, **arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Format response
        import json
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
        ]


# Global server instance
mcp_server = SevOneMCPServerSSE()


async def handle_sse(request):
    """Handle SSE connection"""
    async with SseServerTransport("/messages") as transport:
        await mcp_server.server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.server.create_initialization_options()
        )


async def handle_messages(request):
    """Handle message endpoint"""
    # This is handled by the SSE transport
    pass


def create_app():
    """Create Starlette application"""
    return Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SevOne MCP Server with SSE transport")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8444, help="Port to bind to")
    args = parser.parse_args()
    
    try:
        # Initialize server
        await mcp_server.initialize()
        
        # Create and run app
        app = create_app()
        
        logger.info(f"Starting SSE server on {args.host}:{args.port}")
        logger.info(f"SSE endpoint: http://{args.host}:{args.port}/sse")
        logger.info(f"Messages endpoint: http://{args.host}:{args.port}/messages")
        
        import uvicorn
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            log_level=log_level.lower()
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
