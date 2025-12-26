"""
Risk Analysis Service.

This module provides the application service for risk analysis,
coordinating building and transaction data retrieval with risk evaluation.
"""
from typing import List
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore
from modules.risk_analysis.domain.rules import (
    ViolationCheckRule,
    SeismicDesignRule,
    BuildingAgeRule,
    PriceDeviationRule,
    RiskEvaluator
)


class RiskAnalysisService:
    """
    Application service for risk analysis.

    This service coordinates the entire risk analysis workflow:
    1. Create building and transaction information
    2. Evaluate risk using domain rules
    3. Return comprehensive risk score

    For MVP, this is simplified to work with direct BuildingInfo and TransactionInfo objects.
    In production, this would fetch data from external APIs.
    """

    def analyze_property(
        self,
        building: BuildingInfo,
        transaction: TransactionInfo,
        house_platform_id: str,
        historical_transactions: List[TransactionInfo] = None
    ) -> RiskScore:
        """
        Analyze risk for a property.

        Args:
            building: Building information
            transaction: Current transaction information
            house_platform_id: Unique identifier for the property (FK to house_platform table)
            historical_transactions: List of historical transactions for price comparison

        Returns:
            RiskScore: Comprehensive risk assessment

        Raises:
            ValueError: If house_platform_id is empty
        """
        # Validate input
        if not house_platform_id or house_platform_id.strip() == "":
            raise ValueError("House platform ID cannot be empty")

        # Use empty list if no historical transactions provided
        if historical_transactions is None:
            historical_transactions = []

        # Set up risk evaluation rules
        rules = [
            ViolationCheckRule(),
            SeismicDesignRule(),
            BuildingAgeRule(),
            PriceDeviationRule(historical_transactions)
        ]

        # Evaluate risk
        evaluator = RiskEvaluator(rules)
        risk_score = evaluator.evaluate(building, transaction, house_platform_id)

        return risk_score
