import os
import yaml
from typing import Dict, Any

from dotenv import find_dotenv, load_dotenv

from src.infrastructure.di import inject


@inject
class ConfigReader:
    """
    Configuration reader for loading and managing application settings.

    Reads env_type from .env (e.g. env_type=development).
    Uses appsettings.development.yaml when env_type=development,
    otherwise appsettings.yaml.
    """
    __di_singleton__ = True
    
    _instance = None
    _config = None
    _dotenv_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigReader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()

    @classmethod
    def _ensure_dotenv_loaded(cls) -> None:
        if cls._dotenv_loaded:
            return
        dotenv_path = find_dotenv(usecwd=True)
        if dotenv_path:
            load_dotenv(dotenv_path)
        cls._dotenv_loaded = True

    @classmethod
    def _resolve_config_path(cls) -> str:
        cls._ensure_dotenv_loaded()
        env_type = os.getenv("env_type", "development").strip().lower()
        if env_type == "development":
            return "./res/appsettings.development.yaml"
        return "./res/appsettings.yaml"
    
    def _load_config(self):
        """Load configuration from the environment-specific appsettings file"""
        config_path = self._resolve_config_path()
        try:            
            with open(config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
                
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {str(e)}")
            # Fallback to default configuration
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if appsettings file is not available"""
        return {
            "app": {
                "name": "Plugin Service API",
                "version": "1.0.0",
                "description": "Your plugin apis",
                "environment": "development"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            },
            "api": {
                "prefix": "/api/v1",
                "cors": {
                    "allow_origins": ["*"],
                    "allow_credentials": True,
                    "allow_methods": ["*"],
                    "allow_headers": ["*"]
                }
            },
            "vaulthc": {
                "enabled": False,
                "KV_VERSION": "1",
                "VAULT_HOST": "",
                "KV_NAMESPACE": "secret",
            },
            "health_check": {
                "enabled": True,
                "timeout": 30
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation (e.g., 'app.version')
        
        Args:
            key: Configuration key in dot notation
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key.split('.')
            value = self._config
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def get_app_version(self) -> str:
        """Get application version"""
        return self.get('app.version', '1.0.0')
    
    def get_app_name(self) -> str:
        """Get application name"""
        return self.get('app.name', 'Plugin Service API')
    
    def get_app_description(self) -> str:
        """Get application description"""
        return self.get('app.description', 'Your plugin apis')
    
    def get_server_host(self) -> str:
        """Get server host"""
        return self.get('server.host', '0.0.0.0')
    
    def get_server_port(self) -> int:
        """Get server port"""
        return self.get('server.port', 5000)
    
    def get_api_prefix(self) -> str:
        """Get API prefix"""
        return self.get('api.prefix', '/api/v1')
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return self.get('api.cors', {})
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration"""
        return self.get('health_check', {})

    def is_vault_enabled(self) -> bool:
        """Whether Vault should be used for secrets (false = use env vars)."""
        return bool(self.get('vaulthc.enabled', False))
    
    def reload(self):
        """Reload configuration from file"""
        self._config = None
        self._load_config()
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary"""
        return self._config.copy()
