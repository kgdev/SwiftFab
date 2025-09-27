# Shopify Configuration Quick Reference

## 🚀 Quick Setup (5 minutes)

### 1. Get Your Shop Domain
- Your Shopify store URL: `https://your-store-name.myshopify.com`
- Your shop domain: `your-store-name.myshopify.com`

### 2. Create Private App
1. Go to: `https://your-store-name.myshopify.com/admin/apps`
2. Click "App and sales channel settings"
3. Click "Develop apps" → "Create an app"
4. Name: "SwiftFab Quote System"
5. Click "Configure Admin API scopes"
6. Enable: `read_products`, `write_products`, `read_orders`, `write_orders`, `read_checkouts`, `write_checkouts`, `read_customers`, `write_customers`
7. Click "Install app"
8. Click "API credentials" tab
9. Copy the "Admin API access token" (starts with `shpat_`)

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
    "api_version": "2024-01"
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
| `access_token` | Private app → API credentials | `shpat_1234567890abcdef...` |
| `api_version` | Use latest stable | `2024-01` |

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
