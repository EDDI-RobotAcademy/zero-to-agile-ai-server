"""
Application configuration module.

Manages environment variables and application settings using pydantic-settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Public Data Portal API Configuration
    PUBLIC_DATA_API_KEY: str = ""
    BUILDING_LEDGER_API_ENDPOINT: str = "http://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
    TRANSACTION_PRICE_API_ENDPOINT: str = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields from .env not defined in Settings
    )


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get settings instance (singleton pattern).

    Returns:
        Settings: Application settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
