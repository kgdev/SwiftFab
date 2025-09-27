"""
Shopify Client Credentials Authentication Module

This module handles client credentials grant authentication with Shopify APIs,
including token acquisition and refresh functionality.
"""

import os
import json
import logging
import requests
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger(__name__)

class ShopifyOAuth:
    """Handle Shopify client credentials grant authentication"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        shopify_config = self.config.get_shopify_config()
        
        self.shop_domain = shopify_config['shop_domain']
        self.client_id = shopify_config['client_id']
        self.client_secret = shopify_config['client_secret']
        self.api_version = shopify_config['api_version']
        
        # Token storage
        self.access_token = None
        self.token_expires_at = None
        self.scope = None
        
        logger.info(f"Shopify client credentials authentication initialized for shop: {self.shop_domain}")
    
    def get_access_token(self) -> Optional[Dict[str, Any]]:
        """
        Get access token using client credentials grant
        
        Returns:
            Token information or None if failed
        """
        try:
            token_url = f"https://{self.shop_domain}/admin/oauth/access_token"
            
            # Client credentials grant request
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Store token information
                self.access_token = token_data.get('access_token')
                self.scope = token_data.get('scope', '')
                
                # Calculate expiration (tokens last 24 hours = 86399 seconds)
                expires_in = token_data.get('expires_in', 86399)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                logger.info(f"Successfully obtained access token for shop: {self.shop_domain}")
                logger.info(f"Token expires at: {self.token_expires_at}")
                logger.info(f"Token scopes: {self.scope}")
                
                return {
                    'access_token': self.access_token,
                    'expires_at': self.token_expires_at.isoformat(),
                    'scope': self.scope,
                    'expires_in': expires_in
                }
            else:
                logger.error(f"Client credentials grant failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    def refresh_access_token(self) -> Optional[Dict[str, Any]]:
        """
        Refresh the access token using client credentials grant
        
        Returns:
            Token information or None if failed
        """
        logger.info("Refreshing access token...")
        return self.get_access_token()
    
    def get_valid_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary
        
        Returns:
            Valid access token or None
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):  # 5 min buffer
                return self.access_token
        
        # Token is expired or doesn't exist, get a new one
        logger.info("Access token expired or missing, getting new token...")
        token_data = self.get_access_token()
        
        if token_data:
            return self.access_token
        else:
            logger.error("Failed to get new access token")
            return None
    
    def make_authenticated_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """
        Make an authenticated request to Shopify Admin API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional request parameters
            
        Returns:
            Response object or None if failed
        """
        access_token = self.get_valid_access_token()
        if not access_token:
            logger.error("No valid access token available for API request")
            return None
        
        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/{endpoint}"
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
        
        # Merge with any existing headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Error making authenticated request: {str(e)}")
            return None
    
    def test_connection(self) -> Optional[Dict[str, Any]]:
        """
        Test the OAuth connection and get shop information
        
        Returns:
            Shop information if connection is working, None otherwise
        """
        try:
            response = self.make_authenticated_request('GET', 'shop.json')
            
            if response and response.status_code == 200:
                shop_data = response.json()
                logger.info(f"OAuth connection test successful for shop: {shop_data.get('shop', {}).get('name', 'Unknown')}")
                return shop_data
            else:
                logger.error(f"OAuth connection test failed: {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            logger.error(f"OAuth connection test error: {str(e)}")
            return None

# Convenience function for getting OAuth instance
def get_oauth_instance(config_path: Optional[str] = None) -> ShopifyOAuth:
    """Get a ShopifyOAuth instance"""
    return ShopifyOAuth(config_path)


def main():
    """
    Main function to test Shopify OAuth connection
    """
    print("🔐 Testing Shopify OAuth Connection")
    print("=" * 40)
    
    try:
        # Initialize OAuth
        oauth = ShopifyOAuth()
        print("✅ OAuth instance initialized successfully")
        print(f"   Shop Domain: {oauth.shop_domain}")
        print(f"   API Version: {oauth.api_version}")
        print(f"   Client ID: {oauth.client_id[:10]}..." if oauth.client_id else "   Client ID: Not configured")
        print(f"   Client Secret: {'Configured' if oauth.client_secret else 'Not configured'}")
        
        # Test token acquisition
        print("\n🎫 Testing Token Acquisition...")
        token_data = oauth.get_access_token()
        if token_data:
            print("✅ Token acquisition successful")
            print(f"   Access Token: {oauth.access_token[:20]}..." if oauth.access_token else "   No access token")
            print(f"   Expires At: {oauth.token_expires_at}")
            print(f"   Scopes: {oauth.scope}")
        else:
            print("❌ Token acquisition failed")
            return False
        
        # Test connection
        print("\n🔗 Testing API Connection...")
        shop_data = oauth.test_connection()
        if shop_data:
            print("✅ API connection successful")
            shop_info = shop_data.get('shop', {})
            print(f"   Shop Name: {shop_info.get('name', 'Unknown')}")
            print(f"   Shop Domain: {shop_info.get('domain', 'Unknown')}")
            print(f"   Shop Email: {shop_info.get('email', 'Unknown')}")
            print(f"   Currency: {shop_info.get('currency', 'Unknown')}")
            print(f"   Timezone: {shop_info.get('timezone', 'Unknown')}")
        else:
            print("❌ API connection failed")
            return False
        
        # Test token refresh
        print("\n🔄 Testing Token Refresh...")
        refreshed_token = oauth.get_valid_access_token()
        if refreshed_token:
            print("✅ Token refresh successful")
            print(f"   Refreshed Token: {refreshed_token[:20]}...")
        else:
            print("❌ Token refresh failed")
            return False
        
        print("\n🎉 All OAuth tests passed! Shopify authentication is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ OAuth test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
