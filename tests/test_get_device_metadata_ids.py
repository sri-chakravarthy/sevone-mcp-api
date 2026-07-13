"""Test script for get_device_metadata_ids tool"""

import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth.credentials import CredentialManager
from auth.token_manager import TokenManager
from api.client import SevOneAPIClient
from tools.get_device_metadata_ids import GetDeviceMetadataIdsTool


async def test_get_device_metadata_ids():
    """Test the get_device_metadata_ids tool"""
    
    print("=" * 60)
    print("Testing get_device_metadata_ids Tool")
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
        print("\n2. Initializing get_device_metadata_ids tool...")
        tool = GetDeviceMetadataIdsTool()
        print(f"✓ Tool name: {tool.name}")
        print(f"✓ Tool description: {tool.description[:100]}...")
        
        # Test 1: Get metadata for specific devices by IDs
        print("\n3. Test 1: Get metadata for devices by IDs...")
        print("   Note: Using device IDs [1, 2] as examples")
        result1 = await tool.execute(
            api_client,
            device_ids=[1, 2],
            page_size=10
        )
        
        if result1["success"]:
            print(f"✓ Success: Retrieved metadata for {result1['data']['total_devices']} device(s)")
            if result1['data']['devices']:
                # Show first device's metadata structure
                first_device_id = list(result1['data']['devices'].keys())[0]
                first_device = result1['data']['devices'][first_device_id]
                print(f"  Device ID: {first_device['device_id']}")
                print(f"  Device Name: {first_device['device_name']}")
                print(f"  Namespaces found: {len(first_device['namespaces'])}")
                
                # Show namespace and attribute details
                for ns_name, ns_data in list(first_device['namespaces'].items())[:2]:
                    print(f"    - Namespace: {ns_name} (ID: {ns_data['namespace_id']})")
                    print(f"      Attributes: {len(ns_data['attributes'])}")
                    for attr_name, attr_data in list(ns_data['attributes'].items())[:2]:
                        print(f"        • {attr_name} (ID: {attr_data['attribute_id']}, Type: {attr_data['attribute_type']})")
        else:
            print(f"✗ Failed: {result1.get('error', 'Unknown error')}")
        
        # Test 2: Get metadata by namespace and attribute name
        print("\n4. Test 2: Get metadata by namespace and attribute name...")
        print("   Note: Using namespace 'System' and attribute 'Location' as example")
        result2 = await tool.execute(
            api_client,
            namespace="System",
            attribute_name="Location",
            page_size=5
        )
        
        if result2["success"]:
            print(f"✓ Success: Retrieved metadata for {result2['data']['total_devices']} device(s)")
            if result2['data']['devices']:
                # Show devices with this specific attribute
                for device_id, device_data in list(result2['data']['devices'].items())[:3]:
                    print(f"  Device: {device_data['device_name']} (ID: {device_id})")
                    if 'System' in device_data['namespaces']:
                        system_ns = device_data['namespaces']['System']
                        if 'Location' in system_ns['attributes']:
                            location_attr = system_ns['attributes']['Location']
                            print(f"    Location Attribute ID: {location_attr['attribute_id']}")
                            print(f"    Values: {location_attr['values']}")
        else:
            print(f"✗ Failed: {result2.get('error', 'Unknown error')}")
        
        # Test 3: Get metadata for devices with specific namespace and attribute
        print("\n5. Test 3: Get metadata for specific devices with namespace filter...")
        result3 = await tool.execute(
            api_client,
            device_ids=[1],
            namespace="System",
            attribute_name="Location",
            page_size=1
        )
        
        if result3["success"]:
            print(f"✓ Success: Retrieved metadata for {result3['data']['total_devices']} device(s)")
            if result3['data']['devices']:
                device_id = list(result3['data']['devices'].keys())[0]
                device = result3['data']['devices'][device_id]
                print(f"  Device: {device['device_name']} (ID: {device_id})")
                
                # Show the filtered metadata
                if device['namespaces']:
                    for ns_name, ns_data in device['namespaces'].items():
                        print(f"    Namespace: {ns_name} (ID: {ns_data['namespace_id']})")
                        for attr_name, attr_data in ns_data['attributes'].items():
                            print(f"      Attribute: {attr_name}")
                            print(f"        ID: {attr_data['attribute_id']}")
                            print(f"        Type: {attr_data['attribute_type']}")
                            print(f"        Values: {attr_data['values']}")
        else:
            print(f"✗ Failed: {result3.get('error', 'Unknown error')}")
        
        # Test 4: Error handling - no parameters
        print("\n6. Test 4: Error handling (no parameters)...")
        result4 = await tool.execute(api_client)
        
        if not result4["success"]:
            print(f"✓ Correctly handled error: {result4.get('error', 'Unknown error')}")
        else:
            print(f"✗ Should have failed but succeeded")
        
        # Test 5: Error handling - attribute_name without namespace
        print("\n7. Test 5: Error handling (attribute_name without namespace)...")
        result5 = await tool.execute(
            api_client,
            attribute_name="Location"
        )
        
        if not result5["success"]:
            print(f"✓ Correctly handled error: {result5.get('error', 'Unknown error')}")
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
    success = asyncio.run(test_get_device_metadata_ids())
    sys.exit(0 if success else 1)

# Made with Bob