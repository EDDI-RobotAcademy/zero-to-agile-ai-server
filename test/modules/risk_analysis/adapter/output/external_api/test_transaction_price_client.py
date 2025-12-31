"""
Tests for Transaction Price API Client.

This module tests the TransactionPriceClient class which fetches
real estate transaction price data from the Public Data Portal API.
"""
import pytest
from unittest.mock import patch, MagicMock
from modules.risk_analysis.adapter.output.external_api.transaction_price_client import (
    TransactionPriceClient,
    TransactionPriceAPIError,
    TransactionPriceNotFoundError,
    TransactionPriceRateLimitError
)


class TestTransactionPriceClient:
    """Test suite for TransactionPriceClient."""

    @pytest.fixture
    def client(self):
        """Create a TransactionPriceClient instance for testing."""
        return TransactionPriceClient()

    @pytest.fixture
    def sample_xml_response(self):
        """Sample successful XML response from Transaction Price API."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <response>
          <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
          </header>
          <body>
            <items>
              <item>
                <dealAmount>50,000</dealAmount>
                <buildYear>2015</buildYear>
                <dealYear>2024</dealYear>
                <dealMonth>11</dealMonth>
                <dealDay>15</dealDay>
                <exclusiveArea>84.5</exclusiveArea>
                <jibun>123-45</jibun>
                <aptNm>마포아파트</aptNm>
                <floor>5</floor>
              </item>
            </items>
          </body>
        </response>"""

    @pytest.fixture
    def multiple_transactions_xml(self):
        """Sample XML response with multiple transaction records."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <response>
          <header>
            <resultCode>00</resultCode>
            <resultMsg>NORMAL SERVICE.</resultMsg>
          </header>
          <body>
            <items>
              <item>
                <dealAmount>50,000</dealAmount>
                <buildYear>2015</buildYear>
                <dealYear>2024</dealYear>
                <dealMonth>11</dealMonth>
                <dealDay>15</dealDay>
                <exclusiveArea>84.5</exclusiveArea>
              </item>
              <item>
                <dealAmount>52,000</dealAmount>
                <buildYear>2016</buildYear>
                <dealYear>2024</dealYear>
                <dealMonth>11</dealMonth>
                <dealDay>20</dealDay>
                <exclusiveArea>84.5</exclusiveArea>
              </item>
            </items>
          </body>
        </response>"""

    @pytest.fixture
    def error_response_not_found(self):
        """Sample error response when no data is found."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <response>
          <header>
            <resultCode>03</resultCode>
            <resultMsg>NO DATA FOUND</resultMsg>
          </header>
        </response>"""

    @pytest.fixture
    def error_response_rate_limit(self):
        """Sample error response for rate limit exceeded."""
        return """<?xml version="1.0" encoding="UTF-8"?>
        <response>
          <header>
            <resultCode>22</resultCode>
            <resultMsg>LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS ERROR</resultMsg>
          </header>
        </response>"""

    def test_client_initialization_loads_settings(self, client):
        """Test that client initializes with settings from config."""
        assert client.api_key is not None
        assert client.endpoint is not None
        assert "getRTMSDataSvcAptTradeDev" in client.endpoint

    def test_parse_xml_response_extracts_transaction_data(self, client, sample_xml_response):
        """Test that XML response is correctly parsed into transaction data."""
        result = client._parse_xml(sample_xml_response)

        assert len(result) == 1
        assert result[0]['dealAmount'] == "50,000"
        assert result[0]['buildYear'] == "2015"
        assert result[0]['dealYear'] == "2024"
        assert result[0]['dealMonth'] == "11"
        assert result[0]['dealDay'] == "15"
        assert result[0]['exclusiveArea'] == "84.5"

    def test_parse_xml_response_extracts_multiple_transactions(self, client, multiple_transactions_xml):
        """Test that multiple transaction records are correctly parsed."""
        result = client._parse_xml(multiple_transactions_xml)

        assert len(result) == 2
        assert result[0]['dealAmount'] == "50,000"
        assert result[1]['dealAmount'] == "52,000"

    def test_get_transactions_with_valid_parameters(self, client, sample_xml_response):
        """Test get_transactions with valid LAWD_CD and DEAL_YMD."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = sample_xml_response
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = client.get_transactions(lawd_cd="11440", deal_ymd="202411")

            assert len(result) == 1
            assert result[0]['dealAmount'] == "50,000"
            mock_get.assert_called_once()

    def test_get_transactions_raises_error_when_lawd_cd_is_empty(self, client):
        """Test that ValueError is raised when LAWD_CD is empty."""
        with pytest.raises(ValueError, match="lawd_cd is required"):
            client.get_transactions(lawd_cd="", deal_ymd="202411")

    def test_get_transactions_raises_error_when_deal_ymd_is_empty(self, client):
        """Test that ValueError is raised when DEAL_YMD is empty."""
        with pytest.raises(ValueError, match="deal_ymd is required"):
            client.get_transactions(lawd_cd="11440", deal_ymd="")

    def test_parse_xml_raises_not_found_error_on_no_data(self, client, error_response_not_found):
        """Test that NotFoundError is raised when API returns no data."""
        with pytest.raises(TransactionPriceNotFoundError, match="No data found"):
            client._parse_xml(error_response_not_found)

    def test_parse_xml_raises_rate_limit_error(self, client, error_response_rate_limit):
        """Test that RateLimitError is raised when rate limit is exceeded."""
        with pytest.raises(TransactionPriceRateLimitError, match="Rate limit exceeded"):
            client._parse_xml(error_response_rate_limit)

    def test_api_request_timeout_raises_error(self, client):
        """Test that timeout during API request raises appropriate error."""
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.Timeout("Request timed out")

            with pytest.raises(TransactionPriceAPIError, match="Request timeout"):
                client.get_transactions(lawd_cd="11440", deal_ymd="202411")

    def test_api_request_failure_raises_error(self, client):
        """Test that network failure during API request raises appropriate error."""
        with patch('requests.get') as mock_get:
            import requests
            mock_get.side_effect = requests.RequestException("Network error")

            with pytest.raises(TransactionPriceAPIError, match="Request failed"):
                client.get_transactions(lawd_cd="11440", deal_ymd="202411")
