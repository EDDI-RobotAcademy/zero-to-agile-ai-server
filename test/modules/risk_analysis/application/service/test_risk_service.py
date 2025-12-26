"""
Tests for Risk Analysis Service.

This module tests the RiskAnalysisService application service.
"""
import pytest
from datetime import datetime
from modules.risk_analysis.application.service.risk_service import RiskAnalysisService
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore


class TestRiskAnalysisService:
    """Test suite for RiskAnalysisService."""

    @pytest.fixture
    def service(self):
        """Create a RiskAnalysisService instance."""
        return RiskAnalysisService()

    @pytest.fixture
    def sample_building(self):
        """Create sample building data."""
        return BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

    @pytest.fixture
    def sample_transaction(self):
        """Create sample transaction data."""
        return TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

    @pytest.fixture
    def historical_transactions(self):
        """Create sample historical transactions."""
        return [
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-1",
                transaction_date="2024-10-01",
                price=48000,
                area=84.5
            ),
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-2",
                transaction_date="2024-10-15",
                price=52000,
                area=84.5
            ),
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-3",
                transaction_date="2024-11-01",
                price=50000,
                area=84.5
            ),
        ]

    def test_service_can_be_instantiated(self, service):
        """Test that RiskAnalysisService can be instantiated."""
        assert service is not None

    def test_analyze_property_returns_risk_score(
        self,
        service,
        sample_building,
        sample_transaction,
        historical_transactions
    ):
        """Test that analyze_property returns a RiskScore."""
        result = service.analyze_property(
            building=sample_building,
            transaction=sample_transaction,
            house_platform_id="PROP-001",
            historical_transactions=historical_transactions
        )

        assert isinstance(result, RiskScore)
        assert result.house_platform_id == "PROP-001"
        assert result.total_score >= 0.0
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]

    def test_analyze_property_with_empty_property_id_raises_error(
        self,
        service,
        sample_building,
        sample_transaction
    ):
        """Test that analyze_property raises ValueError for empty house_platform_id."""
        with pytest.raises(ValueError, match="House platform ID cannot be empty"):
            service.analyze_property(
                building=sample_building,
                transaction=sample_transaction,
                house_platform_id="",
                historical_transactions=[]
            )

    def test_analyze_property_without_historical_data(
        self,
        service,
        sample_building,
        sample_transaction
    ):
        """Test that analyze_property works without historical transactions."""
        result = service.analyze_property(
            building=sample_building,
            transaction=sample_transaction,
            house_platform_id="PROP-NO-HIST"
        )

        assert isinstance(result, RiskScore)
        assert result.price_deviation_risk == 0.0

    def test_analyze_property_evaluates_all_risk_factors(
        self,
        service,
        sample_building,
        sample_transaction,
        historical_transactions
    ):
        """Test that analyze_property evaluates all risk factors."""
        result = service.analyze_property(
            building=sample_building,
            transaction=sample_transaction,
            house_platform_id="PROP-FULL",
            historical_transactions=historical_transactions
        )

        # Check all risk components exist
        assert hasattr(result, 'violation_risk')
        assert hasattr(result, 'seismic_risk')
        assert hasattr(result, 'age_risk')
        assert hasattr(result, 'price_deviation_risk')
        assert result.total_score == (
            result.violation_risk +
            result.seismic_risk +
            result.age_risk +
            result.price_deviation_risk
        )
