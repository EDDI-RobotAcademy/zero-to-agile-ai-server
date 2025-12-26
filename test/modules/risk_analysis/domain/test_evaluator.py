"""
Tests for Risk Evaluator.

This module tests the RiskEvaluator class that aggregates multiple
risk rules to produce a comprehensive risk assessment.
"""
import pytest
from datetime import datetime
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore
from modules.risk_analysis.domain.rules import (
    ViolationCheckRule,
    SeismicDesignRule,
    BuildingAgeRule,
    PriceDeviationRule,
    RiskEvaluator
)


class TestRiskEvaluator:
    """Test suite for RiskEvaluator."""

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

    @pytest.fixture
    def sample_transaction(self):
        """Create a sample transaction for testing."""
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

    def test_evaluator_with_all_rules(self, sample_building, sample_transaction, historical_transactions):
        """Test that evaluator aggregates all rule scores correctly."""
        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(sample_building, sample_transaction, house_platform_id="PROP-001")

        assert isinstance(result, RiskScore)
        assert result.house_platform_id == "PROP-001"
        assert result.total_score >= 0.0
        assert result.total_score <= 100.0
        assert result.violation_risk == 0.0  # No violation
        assert result.seismic_risk == 0.0  # Has seismic design
        assert result.price_deviation_risk == 0.0  # At average price

    def test_evaluator_determines_low_risk_level(self, historical_transactions):
        """Test that evaluator correctly determines LOW risk level."""
        # Create a low-risk building (new, no violations, seismic design)
        current_year = datetime.now().year
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=f"{current_year - 2}0115",  # 2 years old
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,  # Average price
            area=84.5
        )

        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(building, transaction, house_platform_id="PROP-LOW")

        assert result.risk_level == "LOW"
        assert result.total_score < 30.0

    def test_evaluator_determines_medium_risk_level(self, historical_transactions):
        """Test that evaluator correctly determines MEDIUM risk level."""
        # Create a medium-risk building (old, no seismic design)
        current_year = datetime.now().year
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=f"{current_year - 15}0115",  # 15 years old
            seismic_design=False,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=55000,  # 10% above average
            area=84.5
        )

        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(building, transaction, house_platform_id="PROP-MED")

        assert result.risk_level == "MEDIUM"
        assert 30.0 <= result.total_score < 60.0

    def test_evaluator_determines_high_risk_level(self, historical_transactions):
        """Test that evaluator correctly determines HIGH risk level."""
        # Create a high-risk building (old, violations, no seismic, high price)
        current_year = datetime.now().year
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=f"{current_year - 25}0115",  # 25 years old
            seismic_design=False,
            violation_status="위반",
            structure_type="철근콘크리트구조"
        )
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=75000,  # 50% above average
            area=84.5
        )

        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(building, transaction, house_platform_id="PROP-HIGH")

        assert result.risk_level == "HIGH"
        assert result.total_score >= 60.0

    def test_evaluator_generates_appropriate_warnings(self, historical_transactions):
        """Test that evaluator generates appropriate warning messages."""
        # Create building with multiple risk factors
        current_year = datetime.now().year
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date=f"{current_year - 25}0115",
            seismic_design=False,
            violation_status="위반",
            structure_type="철근콘크리트구조"
        )
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=75000,
            area=84.5
        )

        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(building, transaction, house_platform_id="PROP-WARN")

        assert isinstance(result.warnings, list)
        assert len(result.warnings) > 0
        # Should have warnings for: violation, no seismic design, old building, high price

    def test_evaluator_with_no_rules_returns_zero_score(self, sample_building, sample_transaction):
        """Test that evaluator with no rules returns zero risk score."""
        evaluator = RiskEvaluator([])

        result = evaluator.evaluate(sample_building, sample_transaction, house_platform_id="PROP-EMPTY")

        assert result.total_score == 0.0
        assert result.risk_level == "LOW"
        assert len(result.warnings) == 0

    def test_evaluator_populates_all_risk_score_fields(self, sample_building, sample_transaction, historical_transactions):
        """Test that evaluator populates all RiskScore fields correctly."""
        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        result = evaluator.evaluate(sample_building, sample_transaction, house_platform_id="PROP-FULL")

        # Check all fields are present and have correct types
        assert isinstance(result.house_platform_id, str)
        assert isinstance(result.total_score, float)
        assert isinstance(result.violation_risk, float)
        assert isinstance(result.price_deviation_risk, float)
        assert isinstance(result.seismic_risk, float)
        assert isinstance(result.age_risk, float)
        assert isinstance(result.risk_level, str)
        assert isinstance(result.warnings, list)


class TestRiskEvaluatorIntegration:
    """Integration tests for complete risk evaluation workflow."""

    def test_full_risk_evaluation_workflow(self):
        """
        Integration test for complete risk evaluation workflow.

        This test simulates a real-world scenario where we evaluate
        multiple properties with different risk profiles and verify
        that the system produces accurate, comprehensive risk assessments.
        """
        # Prepare historical transaction data for price deviation calculation
        historical_transactions = [
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-1",
                transaction_date="2024-09-01",
                price=48000,
                area=84.5
            ),
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-2",
                transaction_date="2024-09-15",
                price=50000,
                area=84.5
            ),
            TransactionInfo(
                address="서울특별시 마포구 연남동 100-3",
                transaction_date="2024-10-01",
                price=52000,
                area=84.5
            ),
        ]
        # Average price: 50,000

        # Set up evaluator with all rules
        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]
        evaluator = RiskEvaluator(rules)

        # Test Case 1: LOW RISK - New building, good condition, fair price
        current_year = datetime.now().year
        low_risk_building = BuildingInfo(
            address="서울특별시 마포구 연남동 200-1",
            approval_date=f"{current_year - 3}0315",  # 3 years old
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )
        low_risk_transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 200-1",
            transaction_date="2024-11-20",
            price=51000,  # Close to average (2% above)
            area=84.5
        )

        low_result = evaluator.evaluate(low_risk_building, low_risk_transaction, "PROP-LOW-001")

        assert low_result.risk_level == "LOW"
        assert low_result.total_score < 30.0
        assert low_result.violation_risk == 0.0
        assert low_result.seismic_risk == 0.0
        assert low_result.age_risk == 0.0
        assert low_result.price_deviation_risk == 2.0  # 2% deviation

        # Test Case 2: MEDIUM RISK - Older building, no seismic design, moderate price
        medium_risk_building = BuildingInfo(
            address="서울특별시 마포구 연남동 300-1",
            approval_date=f"{current_year - 12}0620",  # 12 years old
            seismic_design=False,
            violation_status="정상",
            structure_type="철골조"
        )
        medium_risk_transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 300-1",
            transaction_date="2024-11-20",
            price=58000,  # 16% above average
            area=84.5
        )

        medium_result = evaluator.evaluate(medium_risk_building, medium_risk_transaction, "PROP-MED-001")

        assert medium_result.risk_level == "MEDIUM"
        assert 30.0 <= medium_result.total_score < 60.0
        assert medium_result.violation_risk == 0.0
        assert medium_result.seismic_risk == 15.0
        assert medium_result.age_risk == 10.0
        assert medium_result.price_deviation_risk == 16.0
        assert "내진설계 미적용" in medium_result.warnings
        assert "건축물 노후화 (10년 이상)" in medium_result.warnings

        # Test Case 3: HIGH RISK - Old building, violations, high price
        high_risk_building = BuildingInfo(
            address="서울특별시 마포구 연남동 400-1",
            approval_date=f"{current_year - 30}0101",  # 30 years old
            seismic_design=False,
            violation_status="위반",
            structure_type="벽돌조"
        )
        high_risk_transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 400-1",
            transaction_date="2024-11-20",
            price=80000,  # 60% above average (capped at 30)
            area=84.5
        )

        high_result = evaluator.evaluate(high_risk_building, high_risk_transaction, "PROP-HIGH-001")

        assert high_result.risk_level == "HIGH"
        assert high_result.total_score >= 60.0
        assert high_result.violation_risk == 30.0
        assert high_result.seismic_risk == 15.0
        assert high_result.age_risk == 20.0
        assert high_result.price_deviation_risk == 30.0  # Capped at 30
        assert high_result.total_score == 95.0  # 30 + 15 + 20 + 30
        assert "건축물대장 위반 이력 있음" in high_result.warnings
        assert "내진설계 미적용" in high_result.warnings
        assert "건축물 노후화 심각 (20년 이상)" in high_result.warnings
        assert "실거래가 대비 20% 이상 가격 차이" in high_result.warnings

        # Verify all results have different total scores
        assert low_result.total_score < medium_result.total_score < high_result.total_score

        # Verify all required fields are populated
        for result in [low_result, medium_result, high_result]:
            assert result.house_platform_id is not None
            assert result.total_score >= 0.0
            assert result.risk_level in ["LOW", "MEDIUM", "HIGH"]
            assert isinstance(result.warnings, list)
