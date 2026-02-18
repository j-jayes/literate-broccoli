"""
Configuration settings for the lunch ordering system
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure Configuration
    azure_subscription_id: str = "e9b64842-3c87-4665-ad56-86ae7c20fe4b"
    azure_resource_group: str = "rg-lunch-ordering-prod"
    azure_location: str = "eastus"
    
    # Database Configuration
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 86400  # 24 hours
    redis_password: Optional[str] = None
    
    # MS Teams Configuration
    teams_bot_id: Optional[str] = None
    teams_bot_password: Optional[str] = None
    teams_tenant_id: Optional[str] = None
    teams_app_id: Optional[str] = None
    
    # API Configuration
    api_base_url: str = "http://localhost:8000"
    api_secret_key: str
    api_algorithm: str = "HS256"
    api_access_token_expire_minutes: int = 30
    
    # Azure Key Vault
    key_vault_name: Optional[str] = None
    key_vault_uri: Optional[str] = None
    
    # Application Insights
    applicationinsights_connection_string: Optional[str] = None
    application_insights_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    # Web Scraping
    scraper_timeout: int = 30
    scraper_max_retries: int = 3
    selenium_driver_path: str = "/usr/local/bin/chromedriver"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
