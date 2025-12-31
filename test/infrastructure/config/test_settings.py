"""
Test for application settings configuration.

This test ensures that the settings module can load environment variables
for Public Data Portal API keys.
"""
import os
import pytest
from infrastructure.config import get_settings, Settings


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_singleton_returns_same_instance(self):
        """Settings should return the same instance (singleton pattern)."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_settings_loads_public_data_api_key(self, monkeypatch):
        """Settings should load PUBLIC_DATA_API_KEY from environment."""
        test_key = "test_api_key_12345"
        monkeypatch.setenv("PUBLIC_DATA_API_KEY", test_key)

        # Reset singleton for test
        from infrastructure import config
        config._settings = None

        settings = get_settings()
        assert settings.PUBLIC_DATA_API_KEY == test_key

    def test_settings_loads_building_ledger_api_endpoint(self, monkeypatch):
        """Settings should have Building Ledger API endpoint configuration."""
        test_endpoint = "http://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo"
        monkeypatch.setenv("BUILDING_LEDGER_API_ENDPOINT", test_endpoint)

        # Reset singleton for test
        from infrastructure import config
        config._settings = None

        settings = get_settings()
        assert settings.BUILDING_LEDGER_API_ENDPOINT == test_endpoint

    def test_settings_loads_transaction_price_api_endpoint(self, monkeypatch):
        """Settings should have Real Transaction Price API endpoint configuration."""
        test_endpoint = "http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
        monkeypatch.setenv("TRANSACTION_PRICE_API_ENDPOINT", test_endpoint)

        # Reset singleton for test
        from infrastructure import config
        config._settings = None

        settings = get_settings()
        assert settings.TRANSACTION_PRICE_API_ENDPOINT == test_endpoint

    def test_settings_has_default_values(self):
        """Settings should have sensible default values."""
        # Reset singleton for test
        from infrastructure import config
        config._settings = None

        settings = get_settings()

        # Check that attributes exist (may use defaults)
        assert hasattr(settings, 'PUBLIC_DATA_API_KEY')
        assert hasattr(settings, 'BUILDING_LEDGER_API_ENDPOINT')
        assert hasattr(settings, 'TRANSACTION_PRICE_API_ENDPOINT')
