"""
Tests for BjdongCodeRepository.

This test module validates the data access layer for bjdong code lookups.
"""

import pytest
from unittest.mock import Mock, MagicMock
from modules.risk_analysis.adapter.output.persistence.repository.bjdong_code_repository import BjdongCodeRepository
from modules.risk_analysis.adapter.output.persistence.orm.bjdong_code_orm import BjdongCodeORM


class TestBjdongCodeRepository:
    """Test suite for BjdongCodeRepository."""

    @pytest.fixture
    def repository(self):
        """Create a repository instance."""
        return BjdongCodeRepository()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

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

    def test_find_by_address_components_exact_match(
        self,
        repository,
        mock_db_session,
        sample_bjdong_record
    ):
        """Test finding bjdong code with exact match."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_bjdong_record
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repository.find_by_address_components(
            db=mock_db_session,
            sido="서울특별시",
            sigungu="강남구",
            dong="역삼동"
        )

        # Assert
        assert result is not None
        assert result.full_cd == "1114010400"
        assert result.sido_nm == "서울특별시"
        assert result.sigungu_nm == "강남구"
        assert result.bjdong_nm == "역삼동"
        assert result.del_yn == "1"  # Should be updated to "1"
        mock_db_session.commit.assert_called_once()

    def test_find_by_address_components_sido_variation(
        self,
        repository,
        mock_db_session,
        sample_bjdong_record
    ):
        """Test finding bjdong code with sido name variation (서울시 → 서울특별시)."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_bjdong_record
        mock_db_session.query.return_value = mock_query

        # Execute with short name "서울시"
        result = repository.find_by_address_components(
            db=mock_db_session,
            sido="서울시",
            sigungu="강남구",
            dong="역삼동"
        )

        # Assert
        assert result is not None
        assert result.full_cd == "1114010400"
        mock_db_session.query.assert_called_once()

    def test_find_by_address_components_not_found(
        self,
        repository,
        mock_db_session
    ):
        """Test finding bjdong code when no match exists."""
        # Setup mock query to return None
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repository.find_by_address_components(
            db=mock_db_session,
            sido="서울특별시",
            sigungu="강남구",
            dong="존재하지않는동"
        )

        # Assert
        assert result is None
        mock_db_session.commit.assert_not_called()

    def test_find_updates_del_yn_to_1(
        self,
        repository,
        mock_db_session,
        sample_bjdong_record
    ):
        """Test that del_yn is updated to '1' when record is found."""
        # Verify initial state
        assert sample_bjdong_record.del_yn == "0"

        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_bjdong_record
        mock_db_session.query.return_value = mock_query

        # Execute
        result = repository.find_by_address_components(
            db=mock_db_session,
            sido="서울특별시",
            sigungu="강남구",
            dong="역삼동"
        )

        # Assert del_yn was updated
        assert result.del_yn == "1"
        mock_db_session.commit.assert_called_once()

    def test_generate_sido_variations_seoul(self, repository):
        """Test sido variation generation for Seoul."""
        variations = repository._generate_sido_variations("서울시")
        assert "서울시" in variations
        assert "서울특별시" in variations

    def test_generate_sido_variations_busan(self, repository):
        """Test sido variation generation for Busan."""
        variations = repository._generate_sido_variations("부산시")
        assert "부산시" in variations
        assert "부산광역시" in variations

    def test_generate_sido_variations_no_mapping(self, repository):
        """Test sido variation generation when no mapping exists."""
        variations = repository._generate_sido_variations("제주특별자치도")
        assert "제주특별자치도" in variations
        assert len(variations) == 1  # Only original name
