"""
Tests for Risk Analysis Domain Models.

This module tests the domain models: BuildingInfo, TransactionInfo, and RiskScore.
"""
import pytest
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore
from modules.risk_analysis.domain.rules import RiskRule


class TestBuildingInfo:
    """Test suite for BuildingInfo dataclass."""

    def test_building_info_creation_with_all_fields(self):
        """Test that BuildingInfo can be created with all required fields."""
        building = BuildingInfo(
            address="서울특별시 마포구 연남동 123-45",
            approval_date="20200115",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )

        assert building.address == "서울특별시 마포구 연남동 123-45"
        assert building.approval_date == "20200115"
        assert building.seismic_design is True
        assert building.violation_status == "정상"
        assert building.structure_type == "철근콘크리트구조"

    def test_building_info_with_no_seismic_design(self):
        """Test BuildingInfo with seismic_design set to False."""
        building = BuildingInfo(
            address="서울특별시 용산구 이태원동 100-1",
            approval_date="19951201",
            seismic_design=False,
            violation_status="정상",
            structure_type="철골조"
        )

        assert building.seismic_design is False
        assert building.approval_date == "19951201"

    def test_building_info_with_violation_status(self):
        """Test BuildingInfo with violation status."""
        building = BuildingInfo(
            address="서울특별시 영등포구 여의도동 50",
            approval_date="20100315",
            seismic_design=True,
            violation_status="위반",
            structure_type="철근콘크리트구조"
        )

        assert building.violation_status == "위반"


class TestTransactionInfo:
    """Test suite for TransactionInfo dataclass."""

    def test_transaction_info_creation_with_all_fields(self):
        """Test that TransactionInfo can be created with all required fields."""
        transaction = TransactionInfo(
            address="서울특별시 마포구 연남동 123-45",
            transaction_date="2024-11-15",
            price=50000,
            area=84.5
        )

        assert transaction.address == "서울특별시 마포구 연남동 123-45"
        assert transaction.transaction_date == "2024-11-15"
        assert transaction.price == 50000
        assert transaction.area == 84.5

    def test_transaction_info_with_different_prices(self):
        """Test TransactionInfo with different price values."""
        transaction1 = TransactionInfo(
            address="서울특별시 용산구 이태원동 100-1",
            transaction_date="2024-10-20",
            price=70000,
            area=100.0
        )

        transaction2 = TransactionInfo(
            address="서울특별시 용산구 이태원동 100-1",
            transaction_date="2024-09-15",
            price=65000,
            area=100.0
        )

        assert transaction1.price == 70000
        assert transaction2.price == 65000

    def test_transaction_info_with_decimal_area(self):
        """Test TransactionInfo with decimal area value."""
        transaction = TransactionInfo(
            address="서울특별시 영등포구 여의도동 50",
            transaction_date="2024-08-10",
            price=45000,
            area=59.9
        )

        assert transaction.area == 59.9


class TestRiskScore:
    """Test suite for RiskScore dataclass."""

    def test_risk_score_creation_with_all_fields(self):
        """Test that RiskScore can be created with all required fields."""
        risk_score = RiskScore(
            house_platform_id="PROP-001",
            total_score=45.0,
            violation_risk=0.0,
            price_deviation_risk=15.0,
            seismic_risk=15.0,
            age_risk=15.0,
            risk_level="MEDIUM",
            warnings=["내진설계 미적용", "실거래가 대비 10% 높음"]
        )

        assert risk_score.house_platform_id == "PROP-001"
        assert risk_score.total_score == 45.0
        assert risk_score.violation_risk == 0.0
        assert risk_score.price_deviation_risk == 15.0
        assert risk_score.seismic_risk == 15.0
        assert risk_score.age_risk == 15.0
        assert risk_score.risk_level == "MEDIUM"
        assert len(risk_score.warnings) == 2

    def test_risk_score_with_low_risk_level(self):
        """Test RiskScore with LOW risk level."""
        risk_score = RiskScore(
            house_platform_id="PROP-002",
            total_score=20.0,
            violation_risk=0.0,
            price_deviation_risk=10.0,
            seismic_risk=0.0,
            age_risk=10.0,
            risk_level="LOW",
            warnings=[]
        )

        assert risk_score.total_score == 20.0
        assert risk_score.risk_level == "LOW"
        assert len(risk_score.warnings) == 0

    def test_risk_score_with_high_risk_level(self):
        """Test RiskScore with HIGH risk level."""
        risk_score = RiskScore(
            house_platform_id="PROP-003",
            total_score=75.0,
            violation_risk=30.0,
            price_deviation_risk=20.0,
            seismic_risk=15.0,
            age_risk=10.0,
            risk_level="HIGH",
            warnings=["건축물대장 위반 이력 있음", "내진설계 미적용", "실거래가 대비 15% 높음"]
        )

        assert risk_score.total_score == 75.0
        assert risk_score.risk_level == "HIGH"
        assert len(risk_score.warnings) == 3
        assert "건축물대장 위반 이력 있음" in risk_score.warnings

    def test_risk_score_with_empty_warnings(self):
        """Test RiskScore with empty warnings list."""
        risk_score = RiskScore(
            house_platform_id="PROP-004",
            total_score=25.0,
            violation_risk=0.0,
            price_deviation_risk=15.0,
            seismic_risk=0.0,
            age_risk=10.0,
            risk_level="LOW",
            warnings=[]
        )

        assert isinstance(risk_score.warnings, list)
        assert len(risk_score.warnings) == 0


class TestRiskRule:
    """Test suite for RiskRule abstract interface."""

    def test_risk_rule_is_abstract(self):
        """Test that RiskRule cannot be instantiated directly."""
        with pytest.raises(TypeError):
            RiskRule()

    def test_risk_rule_subclass_must_implement_evaluate(self):
        """Test that subclass must implement evaluate method."""

        # Create a subclass without implementing evaluate
        class IncompleteRule(RiskRule):
            pass

        with pytest.raises(TypeError):
            IncompleteRule()

    def test_risk_rule_subclass_with_evaluate_can_be_instantiated(self):
        """Test that subclass with evaluate method can be instantiated."""

        class ConcreteRule(RiskRule):
            def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
                return 0.0

        rule = ConcreteRule()
        assert isinstance(rule, RiskRule)

        # Test that evaluate can be called
        building = BuildingInfo(
            address="test",
            approval_date="20200101",
            seismic_design=True,
            violation_status="정상",
            structure_type="철근콘크리트구조"
        )
        transaction = TransactionInfo(
            address="test",
            transaction_date="2024-01-01",
            price=50000,
            area=84.5
        )

        score = rule.evaluate(building, transaction)
        assert score == 0.0
