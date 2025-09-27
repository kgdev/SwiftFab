"""
Shopify Integration Module for SwiftFab Quote System
Handles product creation, order management, and checkout flow
"""

import os
import json
import shopify
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShopifyIntegration:
    def __init__(self, config_path: Optional[str] = None):
        """Initialize Shopify connection"""
        # Load configuration
        self.config = Config(config_path)
        shopify_config = self.config.get_shopify_config()
        
        self.shop_domain = shopify_config['shop_domain']
        self.access_token = shopify_config['access_token']
        self.storefront_access_token = shopify_config['storefront_access_token']
        self.api_version = shopify_config['api_version']
        
        # Configure Shopify session
        shopify.ShopifyResource.set_site(f"https://{self.shop_domain}/admin/api/{self.api_version}")
        shopify.ShopifyResource.headers.update({
            'X-Shopify-Access-Token': self.access_token
        })
        
        logger.info(f"Shopify integration initialized for shop: {self.shop_domain}")
    
    def create_or_get_product(self, quote_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create or get a product in Shopify for the quote
        Returns product information including variant ID
        """
        try:
            # Generate product title from quote data
            file_name = quote_data.get('file_name', 'Custom Part')
            quote_id = quote_data.get('id', 'unknown')
            
            product_title = f"Custom Fabricated Part - {file_name}"
            product_handle = f"custom-part-{quote_id.lower()}"
            
            # Check if product already exists
            existing_products = shopify.Product.find(handle=product_handle)
            if existing_products:
                product = existing_products[0]
                logger.info(f"Found existing product: {product.id}")
            else:
                # Create new product
                product = shopify.Product()
                product.title = product_title
                product.body_html = f"""
                <p>Custom fabricated part based on your STEP file: <strong>{file_name}</strong></p>
                <p>Quote ID: {quote_id}</p>
                <p>This is a custom manufactured part. Specifications and pricing are based on your uploaded design.</p>
                <p>For questions about this part, please reference Quote ID: {quote_id}</p>
                """
                product.vendor = "SwiftFab"
                product.product_type = "Custom Fabrication"
                product.handle = product_handle
                product.status = "active"
                product.published = True
                
                # Create variant
                variant = shopify.Variant()
                variant.title = "Default"
                variant.price = str(quote_data.get('total_price', 0))
                variant.sku = f"SWIFT-{quote_id}"
                variant.inventory_management = "shopify"
                variant.inventory_quantity = 1
                variant.requires_shipping = True
                variant.weight = 1.0
                variant.weight_unit = "lb"
                
                product.variants = [variant]
                
                # Save product
                if product.save():
                    logger.info(f"Created new product: {product.id}")
                else:
                    logger.error(f"Failed to create product: {product.errors}")
                    return None
            
            # Return product information
            return {
                'product_id': product.id,
                'variant_id': product.variants[0].id,
                'product_title': product.title,
                'price': float(product.variants[0].price),
                'handle': product.handle
            }
            
        except Exception as e:
            logger.error(f"Error creating/getting product: {str(e)}")
            return None
    
    def create_shopify_transaction(self, quote_data: Dict[str, Any], customer_info: Optional[Dict[str, Any]] = None, transaction_type: str = "checkout") -> Optional[Dict[str, Any]]:
        """
        Create a Shopify transaction (checkout or order) from a quote
        
        Args:
            quote_data: Quote information including parts and pricing
            customer_info: Customer and shipping information
            transaction_type: "checkout" for customer-facing checkout, "order" for direct order
        
        Returns:
            Dictionary with transaction information (checkout_url or order_id)
        """
        try:
            # Get or create product
            product_info = self.create_or_get_product(quote_data)
            if not product_info:
                logger.error("Failed to get product information")
                return None
            
            if transaction_type == "checkout":
                return self._create_checkout(product_info, quote_data, customer_info)
            elif transaction_type == "order":
                return self._create_direct_order(product_info, quote_data, customer_info)
            else:
                logger.error(f"Invalid transaction type: {transaction_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating {transaction_type}: {str(e)}")
            return None
    
    def _create_checkout(self, product_info: Dict[str, Any], quote_data: Dict[str, Any], customer_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Create a customer-facing checkout using Storefront API"""
        try:
            # Create checkout using Storefront API
            checkout_data = {
                "lineItems": [
                    {
                        "variantId": f"gid://shopify/ProductVariant/{product_info['variant_id']}",
                        "quantity": 1
                    }
                ],
                "allowPartialAddresses": True,
                "shippingAddress": customer_info.get('shipping_address') if customer_info else None,
                "email": customer_info.get('email') if customer_info else None,
                "note": f"Quote ID: {quote_data.get('id')}\nFile: {quote_data.get('file_name')}"
            }
            
            # Use Storefront API to create checkout
            storefront_url = f"https://{self.shop_domain}/api/{self.api_version}/graphql.json"
            headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Storefront-Access-Token': self.storefront_access_token
            }
            
            mutation = """
            mutation checkoutCreate($input: CheckoutCreateInput!) {
                checkoutCreate(input: $input) {
                    checkout {
                        id
                        webUrl
                        totalPrice {
                            amount
                            currencyCode
                        }
                        lineItems(first: 10) {
                            edges {
                                node {
                                    id
                                    title
                                    quantity
                                    variant {
                                        id
                                        title
                                        price {
                                            amount
                                            currencyCode
                                        }
                                    }
                                }
                            }
                        }
                    }
                    checkoutUserErrors {
                        field
                        message
                    }
                }
            }
            """
            
            import requests
            response = requests.post(
                storefront_url,
                headers=headers,
                json={
                    "query": mutation,
                    "variables": {"input": checkout_data}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and result['data']['checkoutCreate']['checkout']:
                    checkout = result['data']['checkoutCreate']['checkout']
                    logger.info(f"Created checkout: {checkout['id']}")
                    return {
                        'checkout_id': checkout['id'],
                        'checkout_url': checkout['webUrl'],
                        'total_price': checkout['totalPrice']['amount'],
                        'currency': checkout['totalPrice']['currencyCode']
                    }
                else:
                    errors = result['data']['checkoutCreate']['checkoutUserErrors']
                    logger.error(f"Checkout creation errors: {errors}")
                    return None
            else:
                logger.error(f"Failed to create checkout: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating checkout: {str(e)}")
            return None
    
    def _create_direct_order(self, product_info: Dict[str, Any], quote_data: Dict[str, Any], customer_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a direct order using Storefront API (checkout completion)"""
        try:
            # First create a checkout
            checkout_result = self._create_checkout(product_info, quote_data, customer_info)
            if not checkout_result:
                logger.error("Failed to create checkout for order")
                return None
            
            # Complete the checkout to create an order
            checkout_id = checkout_result['checkout_id']
            
            # Use Storefront API to complete checkout
            storefront_url = f"https://{self.shop_domain}/api/{self.api_version}/graphql.json"
            headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Storefront-Access-Token': self.storefront_access_token
            }
            
            # Complete checkout mutation
            mutation = """
            mutation checkoutComplete($checkoutId: ID!) {
                checkoutComplete(checkoutId: $checkoutId) {
                    checkout {
                        id
                        order {
                            id
                            orderNumber
                            totalPrice {
                                amount
                                currencyCode
                            }
                            financialStatus
                            fulfillmentStatus
                        }
                    }
                    checkoutUserErrors {
                        field
                        message
                    }
                }
            }
            """
            
            import requests
            response = requests.post(
                storefront_url,
                headers=headers,
                json={
                    "query": mutation,
                    "variables": {"checkoutId": checkout_id}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'data' in result and result['data']['checkoutComplete']['order']:
                    order = result['data']['checkoutComplete']['order']
                    logger.info(f"Created order from checkout: {order['id']}")
                    return {
                        'order_id': order['id'],
                        'order_number': order['orderNumber'],
                        'total_price': order['totalPrice']['amount'],
                        'currency': order['totalPrice']['currencyCode'],
                        'status': order['financialStatus'],
                        'fulfillment_status': order['fulfillmentStatus']
                    }
                else:
                    errors = result['data']['checkoutComplete']['checkoutUserErrors']
                    logger.error(f"Order creation errors: {errors}")
                    return None
            else:
                logger.error(f"Failed to complete checkout: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None
    
    # Backward compatibility methods
    def create_checkout(self, quote_data: Dict[str, Any], customer_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a Shopify checkout for the quote (backward compatibility)
        """
        return self.create_shopify_transaction(quote_data, customer_info, "checkout")
    
    def create_order_from_quote(self, quote_data: Dict[str, Any], customer_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a direct order in Shopify (backward compatibility)
        """
        return self.create_shopify_transaction(quote_data, customer_info, "order")
    
    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order status from Shopify
        """
        try:
            order = shopify.Order.find(order_id)
            if order:
                return {
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'financial_status': order.financial_status,
                    'fulfillment_status': order.fulfillment_status,
                    'total_price': float(order.total_price),
                    'currency': order.currency,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at
                }
            return None
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}")
            return None
