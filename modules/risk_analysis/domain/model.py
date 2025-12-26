"""
Risk Analysis Domain Models.

This module defines the core domain models for the Risk Analysis module:
- BuildingInfo: Represents building information from the Building Ledger API
- TransactionInfo: Represents transaction data from the Real Transaction Price API
- RiskScore: Represents the risk evaluation result for a property
"""
from dataclasses import dataclass
from typing import List


@dataclass
class BuildingInfo:
    """
    Building information from the Building Ledger API.

    Attributes:
        address: Full address of the building (주소)
        approval_date: Building approval date in YYYYMMDD format (사용승인일)
        seismic_design: Whether the building has seismic design (내진설계 여부)
        violation_status: Building violation status (위반 여부)
        structure_type: Structure type of the building (구조)
    """
    address: str
    approval_date: str
    seismic_design: bool
    violation_status: str
    structure_type: str


@dataclass
class TransactionInfo:
    """
    Real estate transaction information from the Transaction Price API.

    Attributes:
        address: Full address of the property (주소)
        transaction_date: Transaction date in YYYY-MM-DD format (거래일자)
        price: Transaction price in 만원 (거래금액)
        area: Exclusive area in square meters (전용면적)
    """
    address: str
    transaction_date: str
    price: int
    area: float


@dataclass
class RiskScore:
    """
    Risk evaluation result for a property.

    Attributes:
        house_platform_id: Unique identifier for the property (FK to house_platform table)
        total_score: Total risk score (0-100, higher is riskier)
        violation_risk: Risk score from building violations (0-30)
        price_deviation_risk: Risk score from price deviation (0-30)
        seismic_risk: Risk score from lack of seismic design (0-15)
        age_risk: Risk score from building age (0-20)
        risk_level: Overall risk level (LOW, MEDIUM, HIGH)
        warnings: List of warning messages for the user
    """
    house_platform_id: str
    total_score: float
    violation_risk: float
    price_deviation_risk: float
    seismic_risk: float
    age_risk: float
    risk_level: str
    warnings: List[str]
