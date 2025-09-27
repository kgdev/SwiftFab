"""
Shopify Integration Module for SwiftFab Quote System
Handles product creation, order management, and checkout flow
"""

import os
import json
import base64
import time
import shopify
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path
from config import Config
from shopify_oauth import ShopifyOAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyIntegration:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Shopify connection"""
        # Load configuration
        self.config = Config(config_path)
        
        # Initialize OAuth for internal authentication
        self.oauth = ShopifyOAuth(config_path)
        
        logger.info(f"Shopify integration initialized with client credentials grant for shop: {self.oauth.shop_domain}")
        # Authentication will be handled internally when needed
    
    def _ensure_shopify_session(self) -> bool:
        """
        Ensure Shopify library session is authenticated for Admin API calls
        """
        try:
            access_token = self.oauth.get_valid_access_token()
            if access_token:
                # Set up Shopify session
                shopify.ShopifyResource.set_site(f"https://{self.oauth.shop_domain}/admin/api/{self.oauth.api_version}")
                shopify.ShopifyResource.headers.update({
                    'X-Shopify-Access-Token': access_token
                })
                return True
            else:
                logger.error("Failed to get valid access token for Shopify session")
                return False
        except Exception as e:
            logger.error(f"Error setting up Shopify session: {str(e)}")
            return False
    
    def create_checkout_redirect_url(self, quote_data: Dict[str, Any], customer_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a checkout redirect URL with separate products for each part
        Creates individual products for each part and builds a cart with correct quantities
        """
        try:
            # Ensure Shopify session is authenticated
            if not self._ensure_shopify_session():
                logger.error("Failed to authenticate Shopify session for checkout creation")
                return None
            
            parts = quote_data.get('parts', [])
            if not parts:
                logger.error("No parts found in quote data")
                return None
            
            # Create individual products for each part
            cart_items = []
            total_amount = 0
            
            for part in parts:
                part_product_info = self._create_part_product(quote_data, part)
                if part_product_info:
                    quantity = part.get('quantity', 1)
                    cart_items.append({
                        'variant_id': part_product_info['variant_id'],
                        'quantity': quantity
                    })
                    total_amount += part_product_info['price'] * quantity
                else:
                    logger.error(f"Failed to create product for part: {part.get('part_name', 'Unknown')}")
                    return None
            
            # Build cart URL with all items
            # Format: https://shop.myshopify.com/cart/{variant_id1}:{quantity1},{variant_id2}:{quantity2}
            cart_params = []
            for item in cart_items:
                cart_params.append(f"{item['variant_id']}:{item['quantity']}")
            
            cart_string = ",".join(cart_params)
            checkout_url = f"https://{self.oauth.shop_domain}/cart/{cart_string}"
            
            # Calculate total quantity
            total_quantity = sum(item['quantity'] for item in cart_items)
            
            logger.info(f"Created checkout redirect URL with {len(cart_items)} products: {checkout_url}")
            return {
                'checkout_url': checkout_url,
                'total_quantity': total_quantity,
                'total_amount': str(total_amount),
                'currency': 'USD',  # Default currency
                'method': 'redirect',
                'parts_count': len(cart_items)
            }
                
        except Exception as e:
            logger.error(f"Error creating checkout redirect URL: {str(e)}")
            return None
    
    def _create_part_product(self, quote_data: Dict[str, Any], part: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a separate product for an individual part
        """
        try:
            # Generate product title from part data
            part_name = part.get('part_name', f"Part {part.get('part_index', 'N/A')}")
            quote_id = quote_data.get('id', 'unknown')
            file_name = quote_data.get('file_name', 'Custom Part')
            
            # Create unique product handle with timestamp and part index
            timestamp = int(time.time())
            part_index = part.get('part_index', 0)
            
            # Get current date for title
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            product_title = f"{part_name} - {file_name} ({current_date})"
            product_handle = f"{quote_id.lower()}-part{part_index}-{timestamp}"
            
            logger.info(f"Creating product for part: {part_name} with handle: {product_handle}")
            
            # Create new product
            product = shopify.Product()
            product.title = product_title
            
            # Create detailed part description
            material_type = part.get('material_type', 'N/A')
            material_grade = part.get('material_grade', 'N/A')
            material_thickness = part.get('material_thickness', 'N/A')
            finish = part.get('finish', 'N/A')
            quantity = part.get('quantity', 1)
            unit_price = part.get('unit_price', 0)
            total_price = part.get('total_price', 0)
            
            # Get dimensions if available
            body = part.get('body', {})
            dimensions = "N/A"
            if body:
                length = body.get('lengthIn', 0)
                width = body.get('widthIn', 0)
                height = body.get('heightIn', 0)
                if length and width and height:
                    dimensions = f"{length:.2f}\" × {width:.2f}\" × {height:.2f}\""
            
            product.body_html = f"""
            <p><strong>Custom Fabricated Part</strong></p>
            <p>Part Name: <strong>{part_name}</strong></p>
            <p>Source File: <strong>{file_name}</strong></p>
            <p>Quote ID: {quote_id}</p>
            
            <h3>Part Specifications:</h3>
            <ul>
                <li><strong>Material:</strong> {material_type} {material_grade} ({material_thickness}")</li>
                <li><strong>Finish:</strong> {finish}</li>
                <li><strong>Dimensions:</strong> {dimensions}</li>
                <li><strong>Quantity:</strong> {quantity}</li>
                <li><strong>Unit Price:</strong> ${unit_price:.2f}</li>
                <li><strong>Total Price:</strong> ${total_price:.2f}</li>
            </ul>
            
            <p>This is a custom manufactured part based on your uploaded design. 
            For questions about this part, please reference Quote ID: {quote_id}</p>
            """
            
            product.vendor = "SwiftFab"
            product.product_type = "Custom Fabrication"
            product.handle = product_handle
            product.status = "active"
            product.published = True
            
            # Set shipping information for US delivery
            product.requires_shipping = True
            product.shipping_required = True
            
            # Create variant
            variant = shopify.Variant()
            variant.title = "Default"
            variant.price = str(unit_price)  # Use unit price for individual part
            variant.sku = f"SKU-{quote_id}-P{part_index}"
            variant.inventory_management = "shopify"
            variant.inventory_quantity = 100  # Set high inventory for custom parts
            variant.inventory_policy = "continue"  # Allow backorders
            variant.requires_shipping = True
            variant.weight = 1.0
            variant.weight_unit = "lb"
            
            # Set currency to USD
            variant.currency = "USD"
            
            product.variants = [variant]
            
            # Save product
            if product.save():
                logger.info(f"Created product for part {part_name}: {product.id}")
                
                # Create inventory for the variant
                self._create_inventory_for_variant(variant.id)
                
                # Attach uploaded file to the product (optional for individual parts)
                file_path = quote_data.get('file_path')
                if file_path and os.path.exists(file_path):
                    self._attach_file_to_product(product.id, file_path, quote_data.get('file_name', 'design.step'), quote_id)
                
                return {
                    'product_id': product.id,
                    'variant_id': product.variants[0].id,
                    'product_title': product.title,
                    'price': float(product.variants[0].price),
                    'handle': product.handle,
                    'part_name': part_name
                }
            else:
                logger.error(f"Failed to create product for part {part_name}: {product.errors.full_messages()}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating product for part {part.get('part_name', 'Unknown')}: {str(e)}")
            return None
    
    def _create_inventory_for_variant(self, variant_id: int) -> bool:
        """
        Create inventory for a product variant using the proper Shopify approach
        """
        try:
            # Ensure Shopify session is authenticated
            if not self._ensure_shopify_session():
                logger.error("Failed to authenticate Shopify session for inventory creation")
                return False
            # Get the variant to check if it already has inventory
            variants = shopify.Variant.find(variant_id)
            if not variants:
                logger.error(f"Variant {variant_id} not found")
                return False
            variant = variants[0] if isinstance(variants, list) else variants
            
            # Check if inventory is already set up
            if variant.inventory_quantity > 0:
                logger.info(f"Variant {variant_id} already has inventory: {variant.inventory_quantity}")
                return True
            
            
            # For new variants, Shopify automatically creates an inventory item
            # We just need to set the inventory management and quantity
            variant.inventory_management = "shopify"
            variant.inventory_quantity = 1
            variant.inventory_policy = "continue"  # Allow backorders
            
            if variant.save():
                logger.info(f"Updated variant {variant_id} with inventory management and quantity")
                logger.info(f"Successfully set inventory quantity: 1 unit (with backorder policy)")
                return True
            else:
                logger.error(f"Failed to update variant: {variant.errors.full_messages()}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating inventory for variant {variant_id}: {str(e)}")
            return False

    def _attach_file_to_product(self, product_id: int, file_path: str, original_filename: str, quote_id: str) -> bool:
        """
        Add download link to product description using backend endpoint
        """
        try:
            # Ensure Shopify session is authenticated
            if not self._ensure_shopify_session():
                logger.error("Failed to authenticate Shopify session for file attachment")
                return False
            
            # Check if file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Get the product to update its description
            product = shopify.Product.find(product_id)
            if not product:
                logger.error(f"Product {product_id} not found")
                return False
            
            # Create download link to our backend (in production, use actual domain)
            download_url = f"http://localhost:8000/api/downloadFile/{quote_id}?admin_key={{admin_key}}"
            
            # Add download section to the product description
            download_section = f"""
            <p><strong>Original Design File:</strong></p>
            <p>Download your original STEP file: {original_filename}</p>
            <p>Download URL: {download_url}</p>
            <p><em>Note: You'll need to be logged in to download the file.</em></p>
            """
            
            # Append the download section to existing description
            current_description = product.body_html or ""
            updated_description = current_description + download_section
            
            # Update the product description
            product.body_html = updated_description
            
            if product.save():
                logger.info(f"Successfully added backend download link to product {product_id} description")
                return True
            else:
                logger.error(f"Failed to update product description: {product.errors.full_messages()}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding download link to product {product_id}: {str(e)}")
            return False



def main():
    """
    Main function to test Shopify integration connection
    """
    print("🚀 Testing Shopify Integration Connection")
    print("=" * 50)
    
    try:
        # Initialize integration
        integration = ShopifyIntegration()
        print("✅ Shopify integration initialized successfully")
        print(f"   Shop Domain: {integration.oauth.shop_domain}")
        print(f"   API Version: {integration.oauth.api_version}")
        
        # Test OAuth connection
        print("\n🔐 Testing OAuth Connection...")
        shop_data = integration.oauth.test_connection()
        if shop_data:
            print("✅ OAuth connection successful")
            shop_info = shop_data.get('shop', {})
            print(f"   Shop Name: {shop_info.get('name', 'Unknown')}")
            print(f"   Shop Domain: {shop_info.get('domain', 'Unknown')}")
        else:
            print("❌ OAuth connection failed")
            return False
        
        # Test product creation/getting
        print("\n📦 Testing Product Management...")
        test_quote_data = {
            "id": "test_connection_123",
            "file_name": "test_connection.step",
            "total_price": 100.0,
            "parts": [
                {
                    "id": "part_1",
                    "part_index": 1,
                    "material_type": "Aluminum",
                    "material_grade": "6061-T6",
                    "material_thickness": "0.125",
                    "finish": "No Deburring",
                    "quantity": 1,
                    "price": 50.0
                }
            ]
        }
        
        product_info = integration.create_or_get_product(test_quote_data)
        if product_info:
            print("✅ Product management successful")
            print(f"   Product ID: {product_info['product_id']}")
            print(f"   Variant ID: {product_info['variant_id']}")
            print(f"   Product Title: {product_info['product_title']}")
        else:
            print("❌ Product management failed")
            return False
        
        # Test checkout redirect URL creation
        print("\n🔗 Testing Checkout Redirect URL...")
        customer_info = {
            "email": "test@example.com",
            "country_code": "US"
        }
        
        redirect_result = integration.create_checkout_redirect_url(test_quote_data, customer_info)
        if redirect_result:
            print("✅ Checkout redirect URL creation `successful")
            print(f"   Checkout URL: {redirect_result.get('checkout_url', 'N/A')}")
            print(f"   Total Amount: {redirect_result.get('total_amount', 'N/A')}")
            print(f"   Currency: {redirect_result.get('currency', 'N/A')}")
            print(f"   Method: {redirect_result.get('method', 'N/A')}")
        else:
            print("❌ Checkout redirect URL creation failed")
            return False
        
        print("\n🎉 All tests passed! Shopify integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
