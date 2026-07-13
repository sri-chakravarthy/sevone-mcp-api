"""Test script for get_device_details tool"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.get_device_details import GetDeviceDetailsTool


async def test_get_device_details():
    """Test the get_device_details tool"""
    
    print("=" * 60)
    print("Testing get_device_details Tool")
    print("=" * 60)
    
    try:
        # Initialize credentials and API client
        print("\n1. Initializing authentication...")
        credential_manager = CredentialManager()
        hostname, username, password = credential_manager.get_credentials()
        
        verify_ssl = os.getenv("SEVONE_VERIFY_SSL", "false").lower() == "true"
        
        token_manager = TokenManager(hostname, username, password, verify_ssl=verify_ssl)
        api_client = SevOneAPIClient(token_manager, verify_ssl=verify_ssl)
        
        # Test authentication
        await token_manager.get_token()
        print("✓ Authentication successful")
        
        # Initialize tool
        print("\n2. Initializing get_device_details tool...")
        tool = GetDeviceDetailsTool()
        print(f"✓ Tool name: {tool.name}")
        print(f"✓ Tool description: {tool.description[:100]}...")
        
        # Test 1: Get devices by IDs (example)
        print("\n3. Test 1: Get devices by IDs...")
        print("   Note: Using device IDs [1, 2] as examples")
        result1 = await tool.execute(
            api_client,
            device_ids=[1, 2],
            page_size=10
        )
        
        if result1["success"]:
            print(f"✓ Success: Retrieved {result1['data']['total_count']} device(s)")
            if result1['data']['devices']:
                print(f"  First device: {result1['data']['devices'][0].get('name', 'N/A')}")
        else:
            print(f"✗ Failed: {result1.get('error', 'Unknown error')}")
        
        # Test 2: Get devices by name (fuzzy match)
        print("\n4. Test 2: Get devices by name with fuzzy match...")
        print("   Note: Using wildcard pattern 'router*'")
        result2 = await tool.execute(
            api_client,
            device_names=["router*"],
            fuzzy_match=True,
            page_size=5
        )
        
        if result2["success"]:
            print(f"✓ Success: Retrieved {result2['data']['total_count']} device(s)")
            for i, device in enumerate(result2['data']['devices'][:3], 1):
                print(f"  Device {i}: {device.get('name', 'N/A')}")
        else:
            print(f"✗ Failed: {result2.get('error', 'Unknown error')}")
        
        # Test 3: Get devices with metadata
        print("\n5. Test 3: Get devices with metadata...")
        result3 = await tool.execute(
            api_client,
            device_ids=[1],
            include_metadata=True,
            page_size=1
        )
        
        if result3["success"]:
            print(f"✓ Success: Retrieved {result3['data']['total_count']} device(s)")
            if result3['data']['devices']:
                device = result3['data']['devices'][0]
                print(f"  Device: {device.get('name', 'N/A')}")
                if 'metadata' in device:
                    print(f"  Metadata included: Yes")
                else:
                    print(f"  Metadata included: No")
        else:
            print(f"✗ Failed: {result3.get('error', 'Unknown error')}")
        
        # Test 4: Error handling - no parameters
        print("\n6. Test 4: Error handling (no parameters)...")
        result4 = await tool.execute(api_client)
        
        if not result4["success"]:
            print(f"✓ Correctly handled error: {result4.get('error', 'Unknown error')}")
        else:
            print(f"✗ Should have failed but succeeded")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_get_device_details())
    sys.exit(0 if success else 1)

# Made with Bob