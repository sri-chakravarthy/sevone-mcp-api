"""Test script for get_device_group_details tool"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.get_device_group_details import GetDeviceGroupDetailsTool


async def test_get_device_group_details():
    """Test the get_device_group_details tool"""
    
    print("=" * 80)
    print("Testing get_device_group_details Tool")
    print("=" * 80)
    
    try:
        # Initialize authentication
        print("\n1. Initializing authentication...")
        credential_manager = CredentialManager()
        hostname, username, password = credential_manager.get_credentials()
        
        verify_ssl = os.getenv("SEVONE_VERIFY_SSL", "false").lower() == "true"
        
        token_manager = TokenManager(
            hostname,
            username,
            password,
            verify_ssl=verify_ssl
        )
        
        api_client = SevOneAPIClient(token_manager, verify_ssl=verify_ssl)
        
        # Test authentication
        await token_manager.get_token()
        print("✓ Authentication successful")
        
        # Initialize tool
        print("\n2. Initializing get_device_group_details tool...")
        tool = GetDeviceGroupDetailsTool()
        print(f"✓ Tool initialized: {tool.name}")
        
        # Test 1: Query by device group path
        print("\n3. Test 1: Query by device group path")
        print("-" * 80)
        result = await tool.execute(
            api_client,
            device_group_paths=["All Device Groups/AP/IND"]
        )
        
        print(f"Status: {result['status']}")
        print(f"Total device groups: {result['total_count']}")
        
        if result['device_groups']:
            print(f"\nFirst device group:")
            dg = result['device_groups'][0]
            print(f"  ID: {dg.get('id')}")
            print(f"  Name: {dg.get('name')}")
            print(f"  Path: {' / '.join(dg.get('path', {}).get('pathComponents', []))}")
            print(f"  Description: {dg.get('description', 'N/A')}")
        
        # Test 2: Query by device group IDs (if we have IDs from test 1)
        if result['device_groups'] and len(result['device_groups']) > 0:
            print("\n4. Test 2: Query by device group IDs")
            print("-" * 80)
            
            # Get first device group ID
            dg_id = result['device_groups'][0].get('id')
            
            result2 = await tool.execute(
                api_client,
                device_group_ids=[dg_id]
            )
            
            print(f"Status: {result2['status']}")
            print(f"Total device groups: {result2['total_count']}")
            
            if result2['device_groups']:
                dg = result2['device_groups'][0]
                print(f"\nDevice group details:")
                print(f"  ID: {dg.get('id')}")
                print(f"  Name: {dg.get('name')}")
                print(f"  Path: {' / '.join(dg.get('path', {}).get('pathComponents', []))}")
        
        # Test 3: Query with metadata
        print("\n5. Test 3: Query with metadata included")
        print("-" * 80)
        result3 = await tool.execute(
            api_client,
            device_group_paths=["All Device Groups/AP"],
            include_metadata=True
        )
        
        print(f"Status: {result3['status']}")
        print(f"Total device groups: {result3['total_count']}")
        
        if result3['device_groups']:
            dg = result3['device_groups'][0]
            print(f"\nFirst device group with metadata:")
            print(f"  ID: {dg.get('id')}")
            print(f"  Name: {dg.get('name')}")
            if 'metadata' in dg:
                print(f"  Metadata: {dg['metadata']}")
        
        print("\n" + "=" * 80)
        print("✓ All tests completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_get_device_group_details())

# Made with Bob
