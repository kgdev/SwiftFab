"""
Configuration management for SwiftFab Quote System
Handles loading configuration from JSON files with environment variable fallbacks
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the SwiftFab application"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path"""
        return str(Path(__file__).parent / 'config.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Configuration loaded from: {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file not found at {self.config_path}, using environment variables only")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {self.config_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading config file {self.config_path}: {e}")
            return {}
    
    def get(self, key: str, default: Any = None, section: Optional[str] = None) -> Any:
        """
        Get a configuration value with fallback to environment variables
        
        Args:
            key: Configuration key
            default: Default value if not found
            section: Optional section name (e.g., 'shopify', 'app')
        
        Returns:
            Configuration value or default
        """
        # Try to get from config file first
        if section:
            value = self._config.get(section, {}).get(key)
        else:
            value = self._config.get(key)
        
        if value is not None:
            return value
        
        # Fallback to environment variable
        env_key = f"{section.upper()}_{key.upper()}" if section else key.upper()
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            # Try to parse as JSON for complex values
            try:
                return json.loads(env_value)
            except (json.JSONDecodeError, TypeError):
                return env_value
        
        return default
    
    def get_shopify_config(self) -> Dict[str, Any]:
        """Get Shopify configuration"""
        return {
            'shop_domain': self.get('shop_domain', 'your-shop.myshopify.com', 'shopify'),
            'client_id': self.get('client_id', 'your-client-id', 'shopify'),
            'client_secret': self.get('client_secret', 'your-client-secret', 'shopify'),
            'api_version': self.get('api_version', '2025-07', 'shopify')
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return {
            'debug': self.get('debug', False, 'app'),
            'log_level': self.get('log_level', 'INFO', 'app'),
            'host': self.get('host', '0.0.0.0', 'app'),
            'port': self.get('port', 8000, 'app')
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'url': self.get('url', 'sqlite:///./quotes.db', 'database')
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'admin_key': self.get('admin_key', 'swiftfab_admin_2024', 'security')
        }
    
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()
        logger.info("Configuration reloaded")

# Global configuration instance
config = Config()
