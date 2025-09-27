# Shopify Integration API Reference

This document describes the consolidated Shopify integration methods for the SwiftFab quote system.

## Overview

The Shopify integration has been consolidated into a single, flexible method that handles both checkout and order creation, with backward compatibility for existing code.

## Main Methods

### `create_shopify_transaction()`

**Primary method for creating Shopify transactions from quotes.**

```python
def create_shopify_transaction(
    quote_data: Dict[str, Any], 
    customer_info: Optional[Dict[str, Any]] = None, 
    transaction_type: str = "checkout"
) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `quote_data`: Quote information including parts and pricing
- `customer_info`: Customer and shipping information (optional)
- `transaction_type`: "checkout" or "order" (default: "checkout")

**Returns:**
- Dictionary with transaction information or None if failed

**Transaction Types:**

#### Checkout (`transaction_type="checkout"`)
Creates a customer-facing checkout using Shopify's Storefront API.

**Use Cases:**
- Customer-facing quote checkout
- E-commerce integration
- Public quote purchasing

**Returns:**
```python
{
    'checkout_id': 'gid://shopify/Checkout/...',
    'checkout_url': 'https://checkout.shopify.com/...',
    'total_price': '125.50',
    'currency': 'USD'
}
```

#### Order (`transaction_type="order"`)
Creates a direct order using Shopify's Storefront API (checkout completion).

**Use Cases:**
- Internal order processing
- Automated order creation
- B2B transactions

**Returns:**
```python
{
    'order_id': 123456789,
    'order_number': 1001,
    'total_price': 125.50,
    'currency': 'USD',
    'status': 'pending'
}
```

## Backward Compatibility Methods

### `create_checkout()`

**Legacy method for creating checkouts.**

```python
def create_checkout(
    quote_data: Dict[str, Any], 
    customer_info: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]
```

**Implementation:**
```python
def create_checkout(self, quote_data, customer_info=None):
    return self.create_shopify_transaction(quote_data, customer_info, "checkout")
```

### `create_order_from_quote()`

**Legacy method for creating orders.**

```python
def create_order_from_quote(
    quote_data: Dict[str, Any], 
    customer_info: Dict[str, Any]
) -> Optional[Dict[str, Any]]
```

**Implementation:**
```python
def create_order_from_quote(self, quote_data, customer_info):
    return self.create_shopify_transaction(quote_data, customer_info, "order")
```

## Supporting Methods

### `create_or_get_product()`

**Creates or retrieves a product in Shopify.**

```python
def create_or_get_product(quote_data: Dict[str, Any]) -> Optional[Dict[str, Any]]
```

**Returns:**
```python
{
    'product_id': 123456789,
    'variant_id': 987654321,
    'product_title': 'Custom Fabricated Part - part.step',
    'price': 125.50
}
```

### `get_order_status()`

**Retrieves order status from Shopify.**

```python
def get_order_status(order_id: str) -> Optional[Dict[str, Any]]
```

**Returns:**
```python
{
    'order_id': 123456789,
    'order_number': 1001,
    'financial_status': 'paid',
    'fulfillment_status': 'fulfilled',
    'total_price': 125.50,
    'currency': 'USD',
    'created_at': '2025-01-15T10:30:00Z',
    'updated_at': '2025-01-15T11:00:00Z'
}
```

## Usage Examples

### Creating a Customer Checkout

```python
from shopify_integration import ShopifyIntegration

integration = ShopifyIntegration()

# Quote data
quote_data = {
    'id': 'qte_ABC123',
    'file_name': 'custom-part.step',
    'total_price': 125.50,
    'parts': [...]
}

# Customer information
customer_info = {
    'email': 'customer@example.com',
    'first_name': 'John',
    'last_name': 'Doe',
    'shipping_address': {
        'first_name': 'John',
        'last_name': 'Doe',
        'address1': '123 Main St',
        'city': 'Anytown',
        'province': 'CA',
        'country': 'US',
        'zip': '12345'
    }
}

# Create checkout
result = integration.create_shopify_transaction(
    quote_data, 
    customer_info, 
    "checkout"
)

if result:
    print(f"Checkout URL: {result['checkout_url']}")
```

### Creating a Direct Order

```python
# Create direct order
result = integration.create_shopify_transaction(
    quote_data, 
    customer_info, 
    "order"
)

if result:
    print(f"Order ID: {result['order_id']}")
    print(f"Order Number: {result['order_number']}")
```

### Using Legacy Methods

```python
# Legacy checkout creation
checkout_result = integration.create_checkout(quote_data, customer_info)

# Legacy order creation
order_result = integration.create_order_from_quote(quote_data, customer_info)
```

## API Endpoints

### POST `/api/checkout/{quote_id}`

Creates a Shopify transaction for a quote.

**Request Body:**
```json
{
  "customer_info": {
    "email": "customer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  },
  "shipping_address": {
    "first_name": "John",
    "last_name": "Doe",
    "address1": "123 Main St",
    "address2": "",
    "phone": "+1234567890",
    "city": "Anytown",
    "province": "CA",
    "country": "US",
    "zip": "12345"
  },
  "checkout_type": "checkout"
}
```

**Response:**
```json
{
  "success": true,
  "checkout_type": "checkout",
  "data": {
    "checkout_id": "gid://shopify/Checkout/...",
    "checkout_url": "https://checkout.shopify.com/...",
    "total_price": "125.50",
    "currency": "USD"
  }
}
```

### GET `/api/order-status/{order_id}`

Retrieves order status from Shopify.

**Response:**
```json
{
  "success": true,
  "data": {
    "order_id": 123456789,
    "order_number": 1001,
    "financial_status": "paid",
    "fulfillment_status": "fulfilled",
    "total_price": 125.50,
    "currency": "USD",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T11:00:00Z"
  }
}
```

## Error Handling

All methods return `None` on failure and log detailed error information.

**Common Error Scenarios:**
- Invalid quote data
- Missing product information
- Shopify API errors
- Network connectivity issues
- Invalid customer information

**Error Logging:**
```python
logger.error(f"Error creating {transaction_type}: {str(e)}")
```

## Configuration

The integration requires these configuration values:

```json
{
  "shopify": {
    "shop_domain": "your-shop.myshopify.com",
    "access_token": "shpat_...",
    "storefront_access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "api_version": "2025-07"
  }
}
```

**Getting Access Tokens:**
1. Create an app in [Shopify Partners Dev Dashboard](https://partners.shopify.com)
2. Configure API scopes for your app
3. Install the app to your development store
4. Copy tokens from "API credentials" tab

**Environment Variables (fallback):**
- `SHOPIFY_SHOP_DOMAIN`
- `SHOPIFY_ACCESS_TOKEN`
- `SHOPIFY_STOREFRONT_ACCESS_TOKEN`
- `SHOPIFY_API_VERSION`

## Migration Guide

### From Multiple Methods to Consolidated

**Before:**
```python
# Multiple method calls
product_info = integration.create_or_get_product(quote_data)
if checkout_type == "checkout":
    result = integration.create_checkout(quote_data, customer_info)
else:
    result = integration.create_order_from_quote(quote_data, customer_info)
```

**After:**
```python
# Single method call
result = integration.create_shopify_transaction(
    quote_data, 
    customer_info, 
    checkout_type
)
```

### Backward Compatibility

Existing code using `create_checkout()` and `create_order_from_quote()` will continue to work without changes.

## Best Practices

1. **Use the consolidated method** for new code
2. **Handle None returns** for error cases
3. **Provide customer information** for better order management
4. **Use appropriate transaction types** based on use case
5. **Monitor logs** for error details
6. **Test both transaction types** during development
