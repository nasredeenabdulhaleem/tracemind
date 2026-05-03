"""Application configuration management"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False, extra='ignore')
    
    # Database
    database_url: str
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Cloudflare R2
    r2_endpoint: str
    r2_access_key: str
    r2_secret_key: str
    r2_bucket: str
    
    # IBM watsonx.ai
    watsonx_api_key: str
    watsonx_project_id: str
    watsonx_url: str
    
    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:5173"
    
    # File Processing
    max_upload_size: int = 104857600  # 100MB
    temp_dir: str = "/tmp/tracemind"

    # Workflow Timeouts
    max_analysis_time: int = 30
    max_workflow_time: int = 120

    # Rate Limiting (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()

# Made with Bob
