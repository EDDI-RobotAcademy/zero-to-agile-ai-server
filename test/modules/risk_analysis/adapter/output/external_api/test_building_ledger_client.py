"""
Test for Building Ledger API Client.

This test ensures that the Building Ledger API client can:
1. Make HTTP requests with proper parameters
2. Parse XML responses correctly
3. Handle errors gracefully
"""
import pytest
from unittest.mock import Mock, patch
from modules.risk_analysis.adapter.output.external_api.building_ledger_client import (
    BuildingLedgerClient,
    BuildingLedgerAPIError,
    BuildingLedgerRateLimitError,
    BuildingLedgerNotFoundError
)


class TestBuildingLedgerClient:
    """Test suite for BuildingLedgerClient."""

    @pytest.fixture
    def client(self):
        """Create a BuildingLedgerClient instance for testing."""
        return BuildingLedgerClient()

    @pytest.fixture
    def sample_xml_response(self):
        """Sample successful XML response from Building Ledger API."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <platPlc>서울특별시 마포구 연남동 123-45</platPlc>
        <useAprDay>20200115</useAprDay>
        <vlRatEstmTotArea>0</vlRatEstmTotArea>
        <etcStrct>철근콘크리트구조</etcStrct>
        <heit>15.5</heit>
        <strctCdNm>철근콘크리트구조</strctCdNm>
      </item>
    </items>
    <numOfRows>10</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>1</totalCount>
  </body>
</response>"""

    @pytest.fixture
    def sample_error_response(self):
        """Sample error XML response."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header>
    <resultCode>03</resultCode>
    <resultMsg>NO DATA</resultMsg>
  </header>
</response>"""

    @pytest.fixture
    def sample_rate_limit_response(self):
        """Sample rate limit error response."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header>
    <resultCode>22</resultCode>
    <resultMsg>LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS ERROR</resultMsg>
  </header>
</response>"""

    def test_client_initialization_loads_settings(self, client):
        """Client should load API key and endpoint from settings."""
        assert client.api_key is not None
        assert client.endpoint is not None
        assert "getBrRecapTitleInfo" in client.endpoint

    def test_get_building_info_constructs_correct_url(self, client):
        """get_building_info should construct URL with proper parameters."""
        with patch.object(client, '_make_request') as mock_request:
            mock_request.return_value = {"platPlc": "서울특별시 마포구 연남동 123-45"}

            client.get_building_info(
                sigungu_cd="11440",
                bjdong_cd="10100",
                bun="0123",
                ji="0045"
            )

            # Verify the request was made
            mock_request.assert_called_once()
            call_args = mock_request.call_args[1]

            assert call_args['sigungu_cd'] == "11440"
            assert call_args['bjdong_cd'] == "10100"
            assert call_args['bun'] == "0123"
            assert call_args['ji'] == "0045"

    def test_parse_xml_response_extracts_building_data(self, client, sample_xml_response):
        """_parse_xml should extract building information from XML."""
        result = client._parse_xml(sample_xml_response)

        assert result['platPlc'] == "서울특별시 마포구 연남동 123-45"
        assert result['useAprDay'] == "20200115"
        assert result['vlRatEstmTotArea'] == "0"
        assert result['etcStrct'] == "철근콘크리트구조"
        assert result['heit'] == "15.5"
        assert result['strctCdNm'] == "철근콘크리트구조"

    def test_parse_xml_handles_error_response(self, client, sample_error_response):
        """_parse_xml should raise exception for error responses."""
        with pytest.raises(BuildingLedgerNotFoundError) as exc_info:
            client._parse_xml(sample_error_response)

        assert "03" in str(exc_info.value)
        assert "NO DATA" in str(exc_info.value)

    def test_parse_xml_handles_rate_limit_error(self, client, sample_rate_limit_response):
        """_parse_xml should raise rate limit exception."""
        with pytest.raises(BuildingLedgerRateLimitError) as exc_info:
            client._parse_xml(sample_rate_limit_response)

        assert "22" in str(exc_info.value)

    @patch('requests.get')
    def test_make_request_handles_http_errors(self, mock_get, client):
        """_make_request should handle HTTP errors gracefully."""
        # Simulate 500 Internal Server Error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Internal Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(BuildingLedgerAPIError):
            client._make_request(
                sigungu_cd="11440",
                bjdong_cd="10100"
            )

    @patch('requests.get')
    def test_make_request_handles_timeout(self, mock_get, client):
        """_make_request should handle timeout errors."""
        import requests
        mock_get.side_effect = requests.Timeout("Connection timeout")

        with pytest.raises(BuildingLedgerAPIError) as exc_info:
            client._make_request(
                sigungu_cd="11440",
                bjdong_cd="10100"
            )

        assert "timeout" in str(exc_info.value).lower()

    @patch('requests.get')
    def test_get_building_info_success_flow(self, mock_get, client, sample_xml_response):
        """Test complete success flow for get_building_info."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = sample_xml_response
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        result = client.get_building_info(
            sigungu_cd="11440",
            bjdong_cd="10100",
            bun="0123",
            ji="0045"
        )

        # Verify parsed result
        assert result is not None
        assert result['platPlc'] == "서울특별시 마포구 연남동 123-45"
        assert result['useAprDay'] == "20200115"
        assert result['vlRatEstmTotArea'] == "0"

    def test_get_building_info_validates_parameters(self, client):
        """get_building_info should validate required parameters."""
        with pytest.raises(ValueError):
            client.get_building_info(
                sigungu_cd="",  # Empty string should fail
                bjdong_cd="10100"
            )

        with pytest.raises(ValueError):
            client.get_building_info(
                sigungu_cd="11440",
                bjdong_cd=""  # Empty string should fail
            )

    @patch('requests.get')
    def test_client_includes_api_key_in_request(self, mock_get, client, sample_xml_response):
        """Client should include API key in all requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = sample_xml_response
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        client.get_building_info(
            sigungu_cd="11440",
            bjdong_cd="10100"
        )

        # Verify API key was included in params
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'serviceKey' in params
        assert params['serviceKey'] == client.api_key


class TestBuildingLedgerClientIntegration:
    """Integration tests for BuildingLedgerClient with AddressParserService."""

    @pytest.fixture
    def client(self):
        """Create a BuildingLedgerClient instance for testing."""
        return BuildingLedgerClient()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def sample_xml_response(self):
        """Sample successful XML response from Building Ledger API."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <platPlc>서울특별시 강남구 역삼동 777-88</platPlc>
        <useAprDay>20200115</useAprDay>
        <vlRatEstmTotArea>0</vlRatEstmTotArea>
        <etcStrct>철근콘크리트구조</etcStrct>
        <heit>15.5</heit>
        <strctCdNm>철근콘크리트구조</strctCdNm>
      </item>
    </items>
  </body>
</response>"""

    @patch('modules.risk_analysis.adapter.output.external_api.building_ledger_client.requests.get')
    def test_get_building_info_by_address_success(
        self,
        mock_get,
        client,
        mock_db_session,
        sample_xml_response,
        monkeypatch
    ):
        """Test fetching building info using full address string."""
        from modules.risk_analysis.adapter.output.persistence.orm.bjdong_code_orm import BjdongCodeORM

        # Mock the AddressParserService to return proper codes
        sample_bjdong_record = BjdongCodeORM(
            full_cd="1114010400",
            sido_nm="서울특별시",
            sigungu_nm="강남구",
            bjdong_nm="역삼동",
            bjdong_full_nm="서울특별시 강남구 역삼동",
            del_yn="0"
        )

        mock_find = Mock(return_value=sample_bjdong_record)
        monkeypatch.setattr(
            "modules.risk_analysis.application.service.address_parser_service.BjdongCodeRepository.find_by_address_components",
            mock_find
        )

        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = sample_xml_response
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response

        # Execute
        address = "서울시 강남구 역삼동 777-88"
        result = client.get_building_info_by_address(address, mock_db_session)

        # Assert
        assert result is not None
        assert result['platPlc'] == "서울특별시 강남구 역삼동 777-88"
        assert result['useAprDay'] == "20200115"

        # Verify the API was called with correct parameters
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['sigunguCd'] == "11140"  # First 5 digits of full_cd
        assert params['bjdongCd'] == "10400"   # Last 5 digits of full_cd
        assert params['bun'] == "777"
        assert params['ji'] == "88"

    def test_get_building_info_by_address_invalid_address_raises_error(
        self,
        client,
        mock_db_session
    ):
        """Test that invalid address raises AddressParsingError."""
        from modules.risk_analysis.application.service.address_parser_service import AddressParsingError

        invalid_address = "InvalidAddress"

        with pytest.raises(AddressParsingError):
            client.get_building_info_by_address(invalid_address, mock_db_session)

    def test_get_building_info_by_address_code_not_found_raises_error(
        self,
        client,
        mock_db_session,
        monkeypatch
    ):
        """Test that BjdongCodeNotFoundError is raised when code is not found."""
        from modules.risk_analysis.application.service.address_parser_service import BjdongCodeNotFoundError

        # Mock repository to return None
        mock_find = Mock(return_value=None)
        monkeypatch.setattr(
            "modules.risk_analysis.application.service.address_parser_service.BjdongCodeRepository.find_by_address_components",
            mock_find
        )

        address = "서울시 강남구 존재하지않는동 123"

        with pytest.raises(BjdongCodeNotFoundError):
            client.get_building_info_by_address(address, mock_db_session)
