"""Main MCP server for SevOne API integration"""

import asyncio
import logging
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.run_api_endpoint import RunAPIEndpointTool
from tools.get_device_details import GetDeviceDetailsTool
from tools.get_device_group_details import GetDeviceGroupDetailsTool
from tools.get_device_metadata_ids import GetDeviceMetadataIdsTool
from tools.add_devicegroup_rules import AddDeviceGroupRulesTool
from tools.create_device_group import CreateDeviceGroupTool
from tools.get_alerting_policy_details import GetAlertingPolicyDetailsTool
from tools.get_alerting_policy_folder_details import GetAlertingPolicyFolderDetailsTool
from tools.get_object_details import GetObjectDetailsTool
from tools.get_indicator_details import GetIndicatorDetailsTool

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SevOneMCPServer:
    """
    MCP Server for SevOne API integration
    
    Provides secure, authenticated access to SevOne REST API
    through a generic run_api_endpoint tool.
    """
    
    def __init__(self):
        self.server = Server("sevone-api")
        self.credential_manager = None
        self.token_manager = None
        self.api_client = None
        self.run_api_tool = RunAPIEndpointTool()
        self.get_device_details_tool = GetDeviceDetailsTool()
        self.get_device_group_details_tool = GetDeviceGroupDetailsTool()
        self.get_device_metadata_ids_tool = GetDeviceMetadataIdsTool()
        self.add_devicegroup_rules_tool = AddDeviceGroupRulesTool()
        self.create_device_group_tool = CreateDeviceGroupTool()
        self.get_alerting_policy_details_tool = GetAlertingPolicyDetailsTool()
        self.get_alerting_policy_folder_details_tool = GetAlertingPolicyFolderDetailsTool()
        self.get_object_details_tool = GetObjectDetailsTool()
        self.get_indicator_details_tool = GetIndicatorDetailsTool()
        
        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
    
    def initialize(self):
        """Initialize credentials and API client (deferred auth — no network call here)"""
        try:
            logger.info("Initializing SevOne MCP Server...")
            
            # Load and decrypt credentials
            self.credential_manager = CredentialManager()
            hostname, username, password = self.credential_manager.get_credentials()
            
            logger.info(f"Credentials loaded for SevOne: {hostname}")
            
            # Get SSL verification setting
            verify_ssl = os.getenv("SEVONE_VERIFY_SSL", "false").lower() == "true"
            
            # Initialize token manager (no network call yet)
            self.token_manager = TokenManager(
                hostname,
                username,
                password,
                verify_ssl=verify_ssl
            )
            
            # Initialize API client (no network call yet)
            self.api_client = SevOneAPIClient(
                self.token_manager,
                verify_ssl=verify_ssl
            )
            
            logger.info("✓ SevOne MCP Server ready (auth deferred to first tool call)")
            
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
                name=self.get_device_metadata_ids_tool.name,
                description=self.get_device_metadata_ids_tool.description,
                inputSchema=self.get_device_metadata_ids_tool.input_schema
            ),
            Tool(
                name=self.add_devicegroup_rules_tool.name,
                description=self.add_devicegroup_rules_tool.description,
                inputSchema=self.add_devicegroup_rules_tool.input_schema
            ),
            Tool(
                name=self.create_device_group_tool.name,
                description=self.create_device_group_tool.description,
                inputSchema=self.create_device_group_tool.input_schema
            ),
            Tool(
                name=self.get_alerting_policy_details_tool.name,
                description=self.get_alerting_policy_details_tool.description,
                inputSchema=self.get_alerting_policy_details_tool.input_schema
            ),
            Tool(
                name=self.get_alerting_policy_folder_details_tool.name,
                description=self.get_alerting_policy_folder_details_tool.description,
                inputSchema=self.get_alerting_policy_folder_details_tool.input_schema
            ),
            Tool(
                name=self.get_object_details_tool.name,
                description=self.get_object_details_tool.description,
                inputSchema=self.get_object_details_tool.input_schema
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
        elif name == self.get_device_metadata_ids_tool.name:
            result = await self.get_device_metadata_ids_tool.execute(self.api_client, **arguments)
        elif name == self.add_devicegroup_rules_tool.name:
            result = await self.add_devicegroup_rules_tool.execute(self.api_client, **arguments)
        elif name == self.create_device_group_tool.name:
            result = await self.create_device_group_tool.execute(self.api_client, **arguments)
        elif name == self.get_alerting_policy_details_tool.name:
            result = await self.get_alerting_policy_details_tool.execute(self.api_client, **arguments)
        elif name == self.get_alerting_policy_folder_details_tool.name:
            result = await self.get_alerting_policy_folder_details_tool.execute(self.api_client, **arguments)
        elif name == self.get_object_details_tool.name:
            result = await self.get_object_details_tool.execute(self.api_client, **arguments)
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
    
    async def run(self):
        """Run the MCP server"""
        self.initialize()
        
        logger.info("Starting MCP server on stdio...")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    try:
        server = SevOneMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
