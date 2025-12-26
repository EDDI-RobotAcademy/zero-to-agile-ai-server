"""
Tests for Risk Analysis Rules.

This module tests the concrete risk evaluation rules:
ViolationCheckRule, SeismicDesignRule, and BuildingAgeRule.
"""
import pytest
from datetime import datetime
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo
from modules.risk_analysis.domain.rules import (
    RiskRule,
    ViolationCheckRule,
    SeismicDesignRule,
    BuildingAgeRule,
    PriceDeviationRule
)


class TestViolationCheckRule:
    """Test suite for ViolationCheckRule."""

    @pytest.fixture
    def rule(self):
        """Create a ViolationCheckRule instance."""
        return ViolationCheckRule()

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing."""
        return TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

    def test_no_violation_returns_zero(self, rule, sample_transaction):
        """Test that no violation status returns 0 risk score."""
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 0.0

    def test_violation_returns_max_score(self, rule, sample_transaction):
        """Test that violation status returns maximum risk score."""
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="위반",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 30.0

    def test_various_violation_status_strings(self, rule, sample_transaction):
        """Test that rule handles various violation status strings correctly."""
        # Test "정상" variations
        for status in ["정상", "NORMAL", "없음"]:
            building = BuildingInfo(
                address="test",
                approval_date="20200101",
                seismic_design=True,
                violation_status=status,
                structure_type="test"
            )
            if status == "위반":
                assert rule.evaluate(building, sample_transaction) == 30.0
            else:
                assert rule.evaluate(building, sample_transaction) == 0.0


class TestSeismicDesignRule:
    """Test suite for SeismicDesignRule."""

    @pytest.fixture
    def rule(self):
        """Create a SeismicDesignRule instance."""
        return SeismicDesignRule()

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing."""
        return TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

    def test_seismic_design_exists_returns_zero(self, rule, sample_transaction):
        """Test that building with seismic design returns 0 risk score."""
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 0.0

    def test_no_seismic_design_returns_max_score(self, rule, sample_transaction):
        """Test that building without seismic design returns maximum risk score."""
        building = BuildingInfo(
            address="서울특별시 용산구 이태원동 100-1",
            approval_date="19951201",
            seismic_design=False,
            violation_status="정상",
            structure_type="철골조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 15.0


class TestBuildingAgeRule:
    """Test suite for BuildingAgeRule."""

    @pytest.fixture
    def rule(self):
        """Create a BuildingAgeRule instance."""
        return BuildingAgeRule()

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing."""
        return TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

    def test_new_building_less_than_5_years_returns_zero(self, rule, sample_transaction):
        """Test that building less than 5 years old returns 0 risk score."""
        # Building approved 3 years ago
        current_year = datetime.now().year
        approval_date = f"{current_year - 3}0101"

        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=approval_date,
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 0.0

    def test_building_5_to_10_years_returns_5_points(self, rule, sample_transaction):
        """Test that building 5-10 years old returns 5 risk score."""
        # Building approved 7 years ago
        current_year = datetime.now().year
        approval_date = f"{current_year - 7}0601"

        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=approval_date,
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 5.0

    def test_building_10_to_20_years_returns_10_points(self, rule, sample_transaction):
        """Test that building 10-20 years old returns 10 risk score."""
        # Building approved 15 years ago
        current_year = datetime.now().year
        approval_date = f"{current_year - 15}0301"

        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=approval_date,
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 10.0

    def test_building_over_20_years_returns_20_points(self, rule, sample_transaction):
        """Test that building over 20 years old returns 20 risk score."""
        # Building approved 25 years ago
        current_year = datetime.now().year
        approval_date = f"{current_year - 25}1201"

        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=approval_date,
            seismic_design=False,
            violation_status="정상",
            structure_type="벽돌조"
        )

        score = rule.evaluate(building, sample_transaction)
        assert score == 20.0

    def test_building_age_boundary_at_5_years(self, rule, sample_transaction):
        """Test boundary condition at around 5 years."""
        # Building approved about 5 years and 1 month ago to ensure >= 5.0 years
        current_year = datetime.now().year
        approval_date = f"{current_year - 6}1231"  # Approximately 5 years ago

        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=approval_date,
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        score = rule.evaluate(building, sample_transaction)
        # Should be 5.0 as it's >= 5 years
        assert score == 5.0


class TestPriceDeviationRule:
    """Test suite for PriceDeviationRule."""

    @pytest.fixture
    def rule(self):
        """Create a PriceDeviationRule instance with sample historical data."""
        # Sample historical transactions for calculating average
        historical_transactions = [
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
        return PriceDeviationRule(historical_transactions)

    @pytest.fixture
    def sample_building(self):
        """Create a sample building for testing."""
        return BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

    def test_no_deviation_returns_zero(self, rule, sample_building):
        """Test that transaction at average price returns 0 risk score."""
        # Average of 48000, 52000, 50000 = 50000
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

        score = rule.evaluate(sample_building, transaction)
        assert score == 0.0

    def test_small_deviation_returns_proportional_score(self, rule, sample_building):
        """Test that small price deviation returns proportional score."""
        # Average = 50000, price = 55000, deviation = 10%
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=55000,
            area=84.5
        )

        score = rule.evaluate(sample_building, transaction)
        assert score == 10.0

    def test_large_deviation_capped_at_max_score(self, rule, sample_building):
        """Test that large price deviation is capped at 30 points."""
        # Average = 50000, price = 75000, deviation = 50% but capped at 30
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=75000,
            area=84.5
        )

        score = rule.evaluate(sample_building, transaction)
        assert score == 30.0

    def test_negative_deviation_uses_absolute_value(self, rule, sample_building):
        """Test that price below average also returns positive risk score."""
        # Average = 50000, price = 45000, deviation = |-10%| = 10%
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=45000,
            area=84.5
        )

        score = rule.evaluate(sample_building, transaction)
        assert score == 10.0

    def test_empty_historical_data_returns_zero(self, sample_building):
        """Test that rule with no historical data returns 0 risk score."""
        rule = PriceDeviationRule([])

        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

        score = rule.evaluate(sample_building, transaction)
        assert score == 0.0
