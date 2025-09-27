# Configuration Management

The SwiftFab backend uses a flexible configuration system that supports both JSON configuration files and environment variables.

## Configuration Files

### Main Configuration File
- **File**: `config.json`
- **Purpose**: Primary configuration file for the application
- **Status**: Not tracked in git (contains sensitive data)

### Example Configuration File
- **File**: `config.example.json`
- **Purpose**: Template showing all available configuration options
- **Status**: Tracked in git (safe to share)

## Configuration Structure

```json
{
  "shopify": {
    "shop_domain": "your-shop.myshopify.com",
    "access_token": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "api_version": "2024-01"
  },
  "app": {
    "debug": false,
    "log_level": "INFO",
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "url": "sqlite:///./quotes.db"
  },
  "pricing": {
    "default_currency": "USD",
    "tax_rate": 0.08
  },
  "security": {
    "admin_key": "your-admin-key-here"
  }
}
```

## Setup Instructions

1. **Copy the example configuration**:
   ```bash
   cp config.example.json config.json
   ```

2. **Edit the configuration**:
   ```bash
   nano config.json
   ```

3. **Update Shopify settings**:
   - Replace `your-shop.myshopify.com` with your actual Shopify domain
   - Replace `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` with your actual access token
   - Update API version if needed

## Environment Variable Fallbacks

The system automatically falls back to environment variables if configuration values are not found in the config file:

| Config File Key | Environment Variable | Example |
|----------------|---------------------|---------|
| `shopify.shop_domain` | `SHOPIFY_SHOP_DOMAIN` | `my-shop.myshopify.com` |
| `shopify.access_token` | `SHOPIFY_ACCESS_TOKEN` | `shpat_abc123...` |
| `shopify.api_version` | `SHOPIFY_API_VERSION` | `2024-01` |
| `app.debug` | `APP_DEBUG` | `true` |
| `app.log_level` | `APP_LOG_LEVEL` | `DEBUG` |
| `app.host` | `APP_HOST` | `127.0.0.1` |
| `app.port` | `APP_PORT` | `3000` |
| `database.url` | `DATABASE_URL` | `postgresql://...` |
| `pricing.default_currency` | `PRICING_DEFAULT_CURRENCY` | `EUR` |
| `pricing.tax_rate` | `PRICING_TAX_RATE` | `0.19` |
| `security.admin_key` | `SECURITY_ADMIN_KEY` | `your-secure-admin-key` |

## Using Configuration in Code

### Basic Usage
```python
from config import Config

# Load configuration
config = Config()

# Get specific values
shop_domain = config.get('shop_domain', 'default-shop.myshopify.com', 'shopify')
debug_mode = config.get('debug', False, 'app')
```

### Using Predefined Methods
```python
from config import Config

config = Config()

# Get complete configuration sections
shopify_config = config.get_shopify_config()
app_config = config.get_app_config()
database_config = config.get_database_config()
pricing_config = config.get_pricing_config()
security_config = config.get_security_config()
```

### Using Global Configuration
```python
from config import config

# Use the global configuration instance
shop_domain = config.get('shop_domain', 'default', 'shopify')
```

## Configuration Priority

1. **Config file values** (highest priority)
2. **Environment variables** (fallback)
3. **Default values** (lowest priority)

## Security Notes

- Never commit `config.json` to version control
- Use environment variables in production
- Keep access tokens secure
- Use different configurations for different environments

## Troubleshooting

### Configuration Not Loading
- Check file permissions on `config.json`
- Verify JSON syntax is valid
- Check file path is correct

### Environment Variables Not Working
- Ensure variable names are uppercase
- Use underscores instead of dots
- Prefix with section name (e.g., `SHOPIFY_` for shopify section)

### Shopify Integration Issues
- Verify shop domain format: `your-shop.myshopify.com`
- Check access token format: `shpat_` prefix
- Ensure API version is supported
