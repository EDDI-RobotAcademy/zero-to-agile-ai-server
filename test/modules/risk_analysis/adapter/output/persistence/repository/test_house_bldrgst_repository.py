"""
Tests for HouseBldrgstRepository.

This test module validates the repository methods for house_bldrgst table,
including UPSERT functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
from modules.risk_analysis.adapter.output.persistence.repository.house_bldrgst_repository import HouseBldrgstRepository
from modules.risk_analysis.adapter.output.persistence.orm.house_bldrgst_orm import HouseBldrgstORM
from modules.risk_analysis.domain.model import RiskScore


class TestHouseBldrgstRepository:
    """Test suite for HouseBldrgstRepository."""

    @pytest.fixture
    def repository(self):
        """Create a HouseBldrgstRepository instance."""
        return HouseBldrgstRepository()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def sample_risk_score(self):
        """Create a sample RiskScore."""
        return RiskScore(
            house_platform_id="PROP-001",
            total_score=45.0,
            violation_risk=0.0,
            price_deviation_risk=15.0,
            seismic_risk=15.0,
            age_risk=15.0,
            risk_level="MEDIUM",
            warnings=["내진설계 미적용"]
        )

    def test_save_creates_new_record(
        self,
        repository,
        mock_db_session,
        sample_risk_score
    ):
        """Test that save() creates a new record when it doesn't exist."""
        address = "서울특별시 강남구 역삼동 777-88"

        # Mock find_by_house_platform_id to return None (record doesn't exist)
        # Then return the new record after save
        new_record = HouseBldrgstORM(
            house_platform_id=1,
            address=address,
            total_score=45
        )
        repository.find_by_house_platform_id = Mock(return_value=None)

        # Mock db.refresh to set the returned record
        def mock_refresh(obj):
            obj.house_platform_id = 1
            obj.address = address
            obj.total_score = 45
        mock_db_session.refresh = Mock(side_effect=mock_refresh)

        result = repository.save(mock_db_session, sample_risk_score, address)

        # Verify add and commit were called (new record creation)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_save_updates_existing_record(
        self,
        repository,
        mock_db_session,
        sample_risk_score
    ):
        """Test that save() updates existing record on conflict (UPSERT)."""
        address = "서울특별시 강남구 역삼동 777-88"

        # Mock find_by_house_platform_id to return an existing record
        existing_record = HouseBldrgstORM(
            house_platform_id=1,
            address="Old Address",
            total_score=30
        )
        repository.find_by_house_platform_id = Mock(return_value=existing_record)

        result = repository.save(mock_db_session, sample_risk_score, address)

        # Verify the existing record was updated
        assert result is not None
        assert result.address == address
        assert result.total_score == 45
        # Verify commit and refresh were called (update existing record)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(existing_record)

    def test_save_raises_error_for_empty_house_platform_id(
        self,
        repository,
        mock_db_session
    ):
        """Test that save() raises ValueError for empty house_platform_id."""
        invalid_risk_score = RiskScore(
            house_platform_id="",
            total_score=45.0,
            violation_risk=0.0,
            price_deviation_risk=15.0,
            seismic_risk=15.0,
            age_risk=15.0,
            risk_level="MEDIUM",
            warnings=[]
        )

        with pytest.raises(ValueError, match="house_platform_id cannot be empty"):
            repository.save(mock_db_session, invalid_risk_score, "서울시 강남구 역삼동 123")

    def test_find_by_house_platform_id_success(
        self,
        repository,
        mock_db_session
    ):
        """Test that find_by_house_platform_id() returns record when found."""
        expected_record = HouseBldrgstORM(
            house_platform_id=1,
            address="서울특별시 강남구 역삼동 777-88",
            total_score=45
        )

        # Mock the query chain
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = expected_record

        result = repository.find_by_house_platform_id(mock_db_session, 1)

        assert result is not None
        assert result.house_platform_id == 1
        assert result.address == "서울특별시 강남구 역삼동 777-88"
        assert result.total_score == 45

    def test_find_by_house_platform_id_not_found(
        self,
        repository,
        mock_db_session
    ):
        """Test that find_by_house_platform_id() returns None when not found."""
        # Mock the query chain
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = repository.find_by_house_platform_id(mock_db_session, 999)

        assert result is None
