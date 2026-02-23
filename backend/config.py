from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # App settings
    app_name: str = "DepoSafety V2 API"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # Supabase settings
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Cloudflare R2 settings (S3 compatible)
    r2_endpoint_url: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "deposafety-videos"
    r2_region: str = "auto"
    
    # Blockchain settings (Polygon Mumbai)
    polygon_rpc_url: str = "https://rpc-mumbai.maticvigil.com"
    wallet_private_key: str = ""
    contract_address: str = ""
    chain_id: int = 80001  # Mumbai testnet
    
    # SendGrid settings
    sendgrid_api_key: str = ""
    from_email: str = "noreply@deposafety.com"
    
    # Webhook settings
    webhook_secret: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
