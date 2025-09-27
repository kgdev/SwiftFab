# Shopify Configuration Quick Reference

## 🚀 Quick Setup (5 minutes)

### 1. Get Your Shop Domain
- Your Shopify store URL: `https://your-store-name.myshopify.com`
- Your shop domain: `your-store-name.myshopify.com`

### 2. Create App in Dev Dashboard
1. Go to: [partners.shopify.com](https://partners.shopify.com)
2. Sign in or create Partner account (free)
3. Click "Apps" → "Create app"
4. Choose "Custom app"
5. Name: "SwiftFab Quote System"
6. Select your development store
7. Go to "API credentials" tab
8. Enable scopes: `read_products`, `write_products`, `read_orders`, `write_orders`, `read_checkouts`, `write_checkouts`, `read_customers`, `write_customers`
9. Install app to your store
10. Copy "Admin API access token" (starts with `shpat_`)
11. Copy "Storefront API access token" (no prefix)

### 3. Update Configuration
```bash
cp config.example.json config.json
nano config.json
```

Update these values:
```json
{
  "shopify": {
    "shop_domain": "your-store-name.myshopify.com",
    "access_token": "shpat_your_token_here",
    "storefront_access_token": "your_storefront_token_here",
    "api_version": "2025-07"
  }
}
```

### 4. Test Configuration
```bash
python3 test_shopify_config.py
```

## 🔧 Configuration Values

| Value | Where to Find | Example |
|-------|---------------|---------|
| `shop_domain` | Your Shopify store URL | `my-store.myshopify.com` |
| `access_token` | Dev Dashboard → API credentials | `shpat_1234567890abcdef...` |
| `storefront_access_token` | Dev Dashboard → API credentials | `1234567890abcdef...` |
| `api_version` | Use latest stable | `2025-07` |

## 🛠️ Troubleshooting

### ❌ "Invalid Access Token"
- Check token starts with `shpat_`
- Verify app is installed
- Check API permissions

### ❌ "Shop Not Found"
- Verify domain format: `store-name.myshopify.com`
- Check store is active
- No typos in domain

### ❌ "Insufficient Permissions"
- Reinstall the private app
- Check all required scopes are enabled
- Wait a few minutes for permissions to propagate

## 📞 Need Help?

- **Full Guide**: `SHOPIFY_SETUP_GUIDE.md`
- **Test Script**: `python3 test_shopify_config.py`
- **Shopify Docs**: [shopify.dev/docs/api](https://shopify.dev/docs/api)
