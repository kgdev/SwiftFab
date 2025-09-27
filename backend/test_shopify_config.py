#!/usr/bin/env python3
"""
Shopify Configuration Test Script
Tests the Shopify configuration and connection
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from config import Config
    from shopify_integration import ShopifyIntegration
    import shopify
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)

def test_config_loading():
    """Test if configuration loads correctly"""
    print("🔧 Testing configuration loading...")
    
    try:
        config = Config()
        shopify_config = config.get_shopify_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Shop Domain: {shopify_config['shop_domain']}")
        print(f"   API Version: {shopify_config['api_version']}")
        print(f"   Access Token: {shopify_config['access_token'][:10]}...")
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_shopify_connection():
    """Test Shopify API connection"""
    print("\n🔗 Testing Shopify connection...")
    
    try:
        integration = ShopifyIntegration()
        print(f"✅ Shopify integration initialized")
        print(f"   Shop: {integration.shop_domain}")
        print(f"   API Version: {integration.api_version}")
        
        return True
    except Exception as e:
        print(f"❌ Shopify connection failed: {e}")
        return False

def test_shopify_api():
    """Test actual Shopify API calls"""
    print("\n🌐 Testing Shopify API access...")
    
    try:
        # Test basic API access
        shop = shopify.Shop.current()
        print(f"✅ API access successful!")
        print(f"   Shop Name: {shop.name}")
        print(f"   Shop Domain: {shop.domain}")
        print(f"   Shop Email: {shop.email}")
        
        return True
    except Exception as e:
        print(f"❌ API access failed: {e}")
        print("   This might be due to:")
        print("   - Invalid access token")
        print("   - Insufficient permissions")
        print("   - Network connectivity issues")
        return False

def test_permissions():
    """Test if required permissions are available"""
    print("\n🔐 Testing API permissions...")
    
    try:
        # Test product access
        products = shopify.Product.find(limit=1)
        print("✅ Product read permission: OK")
        
        # Test order access
        orders = shopify.Order.find(limit=1)
        print("✅ Order read permission: OK")
        
        # Test customer access
        customers = shopify.Customer.find(limit=1)
        print("✅ Customer read permission: OK")
        
        return True
    except Exception as e:
        print(f"❌ Permission test failed: {e}")
        print("   Required permissions:")
        print("   - read_products")
        print("   - read_orders") 
        print("   - read_customers")
        return False

def main():
    """Run all tests"""
    print("🚀 SwiftFab Shopify Configuration Test")
    print("=" * 50)
    
    # Check if config file exists
    config_file = backend_dir / 'config.json'
    if not config_file.exists():
        print("❌ Configuration file not found!")
        print(f"   Expected: {config_file}")
        print("   Please copy config.example.json to config.json and update with your values")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_config_loading,
        test_shopify_connection,
        test_shopify_api,
        test_permissions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Shopify configuration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        print("\n📖 For help, see: SHOPIFY_SETUP_GUIDE.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
