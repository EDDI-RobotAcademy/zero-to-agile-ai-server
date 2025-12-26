"""
Tests for AddressParserService.

This test module validates the address parsing and bjdong code lookup functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from modules.risk_analysis.application.service.address_parser_service import (
    AddressParserService,
    AddressParsingError,
    BjdongCodeNotFoundError
)
from modules.risk_analysis.adapter.output.persistence.orm.bjdong_code_orm import BjdongCodeORM


class TestAddressParserServiceParsing:
    """Test suite for address parsing functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db_session):
        """Create an AddressParserService instance."""
        return AddressParserService(mock_db_session)

    def test_parse_address_with_bun_and_ji(self, service):
        """Test parsing address with both bun and ji (번-지)."""
        address = "서울시 강남구 역삼동 777-88"

        result = service._parse_address_components(address)

        assert result["sido"] == "서울시"
        assert result["sigungu"] == "강남구"
        assert result["dong"] == "역삼동"
        assert result["bun"] == "777"
        assert result["ji"] == "88"

    def test_parse_address_with_bun_only(self, service):
        """Test parsing address with only bun (번), no ji."""
        address = "서울시 강남구 역삼동 777"

        result = service._parse_address_components(address)

        assert result["sido"] == "서울시"
        assert result["sigungu"] == "강남구"
        assert result["dong"] == "역삼동"
        assert result["bun"] == "777"
        assert result["ji"] is None

    def test_parse_address_no_lot_numbers(self, service):
        """Test parsing address without lot numbers (no bun/ji)."""
        address = "서울시 강남구 역삼동"

        result = service._parse_address_components(address)

        assert result["sido"] == "서울시"
        assert result["sigungu"] == "강남구"
        assert result["dong"] == "역삼동"
        assert result["bun"] is None
        assert result["ji"] is None

    def test_parse_address_with_full_sido_name(self, service):
        """Test parsing address with full sido name (서울특별시)."""
        address = "서울특별시 종로구 효자동 123"

        result = service._parse_address_components(address)

        assert result["sido"] == "서울특별시"
        assert result["sigungu"] == "종로구"
        assert result["dong"] == "효자동"
        assert result["bun"] == "123"

    def test_parse_address_with_ri_instead_of_dong(self, service):
        """Test parsing address with 리 instead of 동."""
        address = "경기도 파주시 교하리 456-12"

        result = service._parse_address_components(address)

        assert result["sido"] == "경기도"
        assert result["sigungu"] == "파주시"
        assert result["dong"] == "교하리"
        assert result["bun"] == "456"
        assert result["ji"] == "12"

    def test_parse_address_invalid_format_raises_error(self, service):
        """Test that invalid address format raises AddressParsingError."""
        invalid_address = "InvalidAddress"

        with pytest.raises(AddressParsingError) as exc_info:
            service._parse_address_components(invalid_address)

        assert "Invalid address format" in str(exc_info.value)

    def test_parse_address_empty_string_raises_error(self, service):
        """Test that empty address string raises AddressParsingError."""
        with pytest.raises(AddressParsingError):
            service._parse_address_components("")


class TestAddressParserServiceIntegration:
    """Test suite for full address parsing and code lookup integration."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_db_session):
        """Create an AddressParserService instance."""
        return AddressParserService(mock_db_session)

    @pytest.fixture
    def sample_bjdong_record(self):
        """Create a sample bjdong code record."""
        record = BjdongCodeORM(
            full_cd="1114010400",
            sido_nm="서울특별시",
            sigungu_nm="강남구",
            bjdong_nm="역삼동",
            bjdong_full_nm="서울특별시 강남구 역삼동",
            del_yn="0"
        )
        return record

    def test_parse_address_and_get_codes_success(
        self,
        service,
        mock_db_session,
        sample_bjdong_record,
        monkeypatch
    ):
        """Test successful address parsing and code retrieval."""
        # Mock repository.find_by_address_components to return sample record
        mock_find = Mock(return_value=sample_bjdong_record)
        monkeypatch.setattr(
            "modules.risk_analysis.application.service.address_parser_service.BjdongCodeRepository.find_by_address_components",
            mock_find
        )

        address = "서울시 강남구 역삼동 777-88"
        result = service.parse_address_and_get_codes(address)

        assert result["sigungu_cd"] == "11140"
        assert result["bjdong_cd"] == "10400"
        assert result["bun"] == "777"
        assert result["ji"] == "88"

    def test_parse_address_and_get_codes_not_found_raises_error(
        self,
        service,
        monkeypatch
    ):
        """Test that BjdongCodeNotFoundError is raised when code is not found."""
        # Mock repository.find_by_address_components to return None
        mock_find = Mock(return_value=None)
        monkeypatch.setattr(
            "modules.risk_analysis.application.service.address_parser_service.BjdongCodeRepository.find_by_address_components",
            mock_find
        )

        address = "서울시 강남구 존재하지않는동 123"

        with pytest.raises(BjdongCodeNotFoundError) as exc_info:
            service.parse_address_and_get_codes(address)

        assert "Legal dong code not found" in str(exc_info.value)

    def test_parse_address_and_get_codes_invalid_full_cd_raises_error(
        self,
        service,
        monkeypatch
    ):
        """Test that ValueError is raised when full_cd format is invalid."""
        # Create a record with invalid full_cd (not 10 digits)
        invalid_record = BjdongCodeORM(
            full_cd="123",  # Invalid: should be 10 digits
            sido_nm="서울특별시",
            sigungu_nm="강남구",
            bjdong_nm="역삼동",
            bjdong_full_nm="서울특별시 강남구 역삼동",
            del_yn="0"
        )

        mock_find = Mock(return_value=invalid_record)
        monkeypatch.setattr(
            "modules.risk_analysis.application.service.address_parser_service.BjdongCodeRepository.find_by_address_components",
            mock_find
        )

        address = "서울시 강남구 역삼동 777"

        with pytest.raises(ValueError) as exc_info:
            service.parse_address_and_get_codes(address)

        assert "Invalid full_cd format" in str(exc_info.value)
