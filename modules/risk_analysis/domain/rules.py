"""
Risk Analysis Rules.

This module defines the abstract base class and concrete implementations
for risk evaluation rules in the Risk Analysis module.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore


class RiskRule(ABC):
    """
    Abstract base class for risk evaluation rules.

    All risk evaluation rules must inherit from this class and implement
    the evaluate method to calculate risk scores based on building and
    transaction information.
    """

    @abstractmethod
    def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
        """
        Evaluate risk score for a property.

        Args:
            building: Building information from Building Ledger API
            transaction: Transaction information from Transaction Price API

        Returns:
            Risk score (0-100 range, higher is riskier)
        """
        pass


class ViolationCheckRule(RiskRule):
    """
    Rule to check building ledger violations.

    Returns 30 points if building has violation status,
    otherwise returns 0 points.
    """

    MAX_SCORE = 30.0

    def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
        """
        Evaluate violation risk score.

        Args:
            building: Building information
            transaction: Transaction information (not used)

        Returns:
            30.0 if violation exists, 0.0 otherwise
        """
        if building.violation_status == "위반":
            return self.MAX_SCORE
        return 0.0


class SeismicDesignRule(RiskRule):
    """
    Rule to check seismic design compliance.

    Returns 15 points if building lacks seismic design,
    otherwise returns 0 points.
    """

    MAX_SCORE = 15.0

    def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
        """
        Evaluate seismic design risk score.

        Args:
            building: Building information
            transaction: Transaction information (not used)

        Returns:
            15.0 if no seismic design, 0.0 otherwise
        """
        if not building.seismic_design:
            return self.MAX_SCORE
        return 0.0


class BuildingAgeRule(RiskRule):
    """
    Rule to evaluate building age risk.

    Returns risk score based on years since approval date:
    - Less than 5 years: 0 points
    - 5-10 years: 5 points
    - 10-20 years: 10 points
    - Over 20 years: 20 points
    """

    def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
        """
        Evaluate building age risk score.

        Args:
            building: Building information
            transaction: Transaction information (not used)

        Returns:
            Risk score based on building age (0, 5, 10, or 20 points)
        """
        try:
            # Parse approval date (YYYYMMDD format)
            approval_date = datetime.strptime(building.approval_date, "%Y%m%d")
            years_old = (datetime.now() - approval_date).days / 365.25

            if years_old < 5:
                return 0.0
            elif years_old < 10:
                return 5.0
            elif years_old < 20:
                return 10.0
            else:
                return 20.0
        except (ValueError, AttributeError):
            # If date parsing fails, return maximum score for safety
            return 20.0


class PriceDeviationRule(RiskRule):
    """
    Rule to evaluate price deviation from market average.

    Calculates risk score based on how much the transaction price deviates
    from the average price of similar properties in the area.
    Score is calculated as: abs(price - avg_price) / avg_price * 100
    Maximum score is capped at 30 points.
    """

    MAX_SCORE = 30.0

    def __init__(self, historical_transactions: List[TransactionInfo]):
        """
        Initialize with historical transaction data.

        Args:
            historical_transactions: List of similar property transactions for comparison
        """
        self.historical_transactions = historical_transactions

    def evaluate(self, building: BuildingInfo, transaction: TransactionInfo) -> float:
        """
        Evaluate price deviation risk score.

        Args:
            building: Building information (not used)
            transaction: Transaction information to evaluate

        Returns:
            Risk score from 0.0 to 30.0 based on price deviation
        """
        # If no historical data, cannot calculate deviation
        if not self.historical_transactions:
            return 0.0

        # Calculate average price from historical transactions
        avg_price = sum(t.price for t in self.historical_transactions) / len(self.historical_transactions)

        # Calculate percentage deviation
        deviation_percentage = abs(transaction.price - avg_price) / avg_price * 100

        # Cap at maximum score
        return min(deviation_percentage, self.MAX_SCORE)


class RiskEvaluator:
    """
    Aggregates multiple risk rules to produce comprehensive risk assessment.

    This class coordinates all risk evaluation rules and combines their
    scores to determine an overall risk level (LOW, MEDIUM, HIGH) along
    with specific warnings for the user.
    """

    def __init__(self, rules: List[RiskRule]):
        """
        Initialize with a list of risk rules.

        Args:
            rules: List of RiskRule instances to apply
        """
        self.rules = rules

    def evaluate(
        self,
        building: BuildingInfo,
        transaction: TransactionInfo,
        house_platform_id: str
    ) -> RiskScore:
        """
        Evaluate comprehensive risk score for a property.

        Args:
            building: Building information from Building Ledger API
            transaction: Transaction information from Transaction Price API
            house_platform_id: Unique identifier for the property (FK to house_platform table)

        Returns:
            RiskScore with total score, individual risk scores, level, and warnings
        """
        # Initialize individual risk scores
        violation_risk = 0.0
        seismic_risk = 0.0
        age_risk = 0.0
        price_deviation_risk = 0.0

        # Evaluate each rule and collect scores
        for rule in self.rules:
            score = rule.evaluate(building, transaction)

            # Categorize score by rule type
            if isinstance(rule, ViolationCheckRule):
                violation_risk = score
            elif isinstance(rule, SeismicDesignRule):
                seismic_risk = score
            elif isinstance(rule, BuildingAgeRule):
                age_risk = score
            elif isinstance(rule, PriceDeviationRule):
                price_deviation_risk = score

        # Calculate total score
        total_score = violation_risk + seismic_risk + age_risk + price_deviation_risk

        # Determine risk level based on total score
        if total_score < 30.0:
            risk_level = "LOW"
        elif total_score < 60.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        # Generate warnings based on individual risk factors
        warnings = []
        if violation_risk > 0:
            warnings.append("건축물대장 위반 이력 있음")
        if seismic_risk > 0:
            warnings.append("내진설계 미적용")
        if age_risk >= 20.0:
            warnings.append("건축물 노후화 심각 (20년 이상)")
        elif age_risk >= 10.0:
            warnings.append("건축물 노후화 (10년 이상)")
        if price_deviation_risk >= 20.0:
            warnings.append("실거래가 대비 20% 이상 가격 차이")
        elif price_deviation_risk >= 15.0:
            warnings.append("실거래가 대비 15% 이상 가격 차이")
        elif price_deviation_risk >= 10.0:
            warnings.append("실거래가 대비 10% 이상 가격 차이")

        return RiskScore(
            house_platform_id=house_platform_id,
            total_score=total_score,
            violation_risk=violation_risk,
            price_deviation_risk=price_deviation_risk,
            seismic_risk=seismic_risk,
            age_risk=age_risk,
            risk_level=risk_level,
            warnings=warnings
        )
