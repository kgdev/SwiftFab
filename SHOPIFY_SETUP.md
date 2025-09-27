# Shopify Integration Setup Guide

This guide will help you set up the Shopify integration for the SwiftFab Quote System to enable checkout functionality.

## Prerequisites

1. A Shopify store (if you don't have one, create one at [shopify.com](https://shopify.com))
2. Admin access to your Shopify store
3. The SwiftFab system running

## Step 1: Create Shopify Apps and Get API Credentials

### 1.1 Create a Private App (Recommended for Development)

1. Go to your Shopify Admin → Apps → App and sales channel settings
2. Click "Develop apps" → "Create an app"
3. Give your app a name (e.g., "SwiftFab Integration")
4. Click "Create app"

### 1.2 Configure API Access

1. In your app settings, go to "Configuration"
2. Set the following:
   - **App URL**: `http://localhost:8000` (for development)
   - **Allowed redirection URL(s)**: `http://localhost:8000/auth/callback`

### 1.3 Get API Credentials

1. Go to "API credentials" tab
2. Click "Install app" to generate credentials
3. Note down:
   - **API key** (this is your `SHOPIFY_ACCESS_TOKEN`)
   - **API secret key** (keep this secure)

### 1.4 Configure Admin API Access Scopes

Enable the following scopes:
- `read_products`
- `write_products`
- `read_orders`
- `write_orders`
- `read_customers`
- `write_customers`
- `read_inventory`
- `write_inventory`

### 1.5 Get Storefront API Access Token (Optional)

1. In your app settings, go to "Storefront API access"
2. Click "Generate token"
3. Note down the **Storefront access token**

## Step 2: Environment Configuration

### 2.1 Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./quotes.db

# Shopify Configuration
SHOPIFY_SHOP_DOMAIN=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-admin-api-access-token
SHOPIFY_API_VERSION=2024-01
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your-storefront-access-token

# Optional: For webhook verification
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
```

### 2.2 Frontend Environment Variables

Create a `.env` file in the `frontend/` directory with the following variables:

```env
# Shopify Configuration
SHOPIFY_DOMAIN=your-shop.myshopify.com
SHOPIFY_STOREFRONT_ACCESS_TOKEN=your-storefront-access-token
```

### 2.2 Replace Placeholder Values

- `your-shop.myshopify.com`: Your Shopify store domain
- `your-admin-api-access-token`: The API key from Step 1.3
- `your-storefront-access-token`: The Storefront API token from Step 1.5 (optional)

## Step 3: Install Dependencies

### 3.1 Backend Dependencies

The Shopify Python API is already added to `requirements.txt`. Install it:

```bash
cd backend
pip install -r requirements.txt
```

### 3.2 Frontend Dependencies

The Shopify Buy SDK is already installed. Install it:

```bash
cd frontend
npm install
```

The following packages are included:
- `shopify-buy`: Official Shopify Storefront API client

## Step 4: Test the Integration

### 4.1 Start the System

```bash
# Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

### 4.2 Test Quote Creation and Checkout

1. Go to `http://localhost:3000`
2. Upload a STEP file to create a quote
3. Configure material settings
4. Click "Proceed to Checkout"
5. Fill in customer and shipping information
6. Choose checkout method:
   - **Shopify Checkout**: Opens Shopify's hosted checkout page
   - **Direct Order**: Creates order directly in Shopify admin

## Step 5: Production Configuration

### 5.1 Update Environment Variables

For production, update your environment variables:

```env
SHOPIFY_SHOP_DOMAIN=your-production-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your-production-access-token
```

### 5.2 Update App URLs

In your Shopify app settings:
- **App URL**: `https://your-domain.com`
- **Allowed redirection URL(s)**: `https://your-domain.com/auth/callback`

### 5.3 SSL Certificate

Ensure your production server has a valid SSL certificate, as Shopify requires HTTPS for production apps.

## Features Overview

### Checkout Flow Options

1. **Shopify Checkout (Recommended)**
   - Uses Shopify's hosted checkout page
   - Handles payment processing
   - Manages customer accounts
   - Provides order tracking

2. **Direct Order Creation**
   - Creates orders directly in Shopify admin
   - Useful for custom payment processing
   - Requires manual payment handling

### Product Management

- Automatically creates products in Shopify for each quote
- Products are named based on the uploaded file
- Pricing is set to the calculated quote total
- Products include quote ID and file information

### Order Tracking

- Orders are linked to the original quote
- Customer information is stored in Shopify
- Order status can be tracked through Shopify admin

## Troubleshooting

### Common Issues

1. **"Invalid API credentials"**
   - Check your `SHOPIFY_ACCESS_TOKEN`
   - Ensure the token has the required scopes
   - Verify the shop domain is correct

2. **"Product creation failed"**
   - Check if the product already exists
   - Verify inventory settings
   - Ensure the product type is valid

3. **"Checkout creation failed"**
   - Check Storefront API access token
   - Verify product variant exists
   - Ensure customer information is complete

### Debug Mode

Enable debug logging by setting the log level in `shopify_integration.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **API Credentials**: Keep your API tokens secure and never commit them to version control
2. **HTTPS**: Always use HTTPS in production
3. **Webhook Verification**: Implement webhook signature verification for production
4. **Rate Limiting**: Be aware of Shopify's API rate limits

## Support

For issues with the Shopify integration:

1. Check the Shopify API documentation
2. Review the application logs
3. Test with Shopify's API testing tools
4. Contact Shopify support for API-related issues

## Next Steps

1. Set up webhook handlers for order updates
2. Implement inventory management
3. Add customer account integration
4. Set up automated order fulfillment
5. Add analytics and reporting
