"""
Test risk analysis with real house_platform data.

This script takes house_platform_id and address from house_platform table,
performs risk analysis, and saves to house_bldrgst table.

Usage:
    python -m scripts.test_risk_with_real_data
"""
import logging
from infrastructure.db.postgres import SessionLocal
from modules.risk_analysis.adapter.output.persistence.repository.house_bldrgst_repository import HouseBldrgstRepository
from modules.house_platform.infrastructure.orm.house_platform_orm import HousePlatformORM
from modules.risk_analysis.domain.model import RiskScore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_risk_score_from_data(house_platform_id: int, address: str) -> RiskScore:
    """
    Create a risk score based on house_platform data.

    Currently uses dummy risk calculation.
    TODO: Replace with real API calls and risk calculation.

    Args:
        house_platform_id: ID from house_platform table
        address: Full address from house_platform table

    Returns:
        RiskScore object
    """
    # For demonstration, create different risk scores based on house_platform_id
    # In production, this would call Building Ledger API and Transaction Price API

    if house_platform_id % 3 == 0:
        # High risk
        return RiskScore(
            house_platform_id=f"PROP-{house_platform_id:03d}",
            total_score=75.0,
            violation_risk=30.0,
            price_deviation_risk=20.0,
            seismic_risk=15.0,
            age_risk=10.0,
            risk_level="HIGH",
            warnings=[
                "건축물대장 위반 이력 있음",
                "내진설계 미적용",
                "실거래가 대비 20% 이상 가격 차이"
            ]
        )
    elif house_platform_id % 3 == 1:
        # Medium risk
        return RiskScore(
            house_platform_id=f"PROP-{house_platform_id:03d}",
            total_score=45.0,
            violation_risk=0.0,
            price_deviation_risk=15.0,
            seismic_risk=15.0,
            age_risk=15.0,
            risk_level="MEDIUM",
            warnings=[
                "내진설계 미적용",
                "건축물 노후화 (10년 이상)"
            ]
        )
    else:
        # Low risk
        return RiskScore(
            house_platform_id=f"PROP-{house_platform_id:03d}",
            total_score=20.0,
            violation_risk=0.0,
            price_deviation_risk=10.0,
            seismic_risk=0.0,
            age_risk=10.0,
            risk_level="LOW",
            warnings=["건축물 노후화 (10년 이상)"]
        )


def main():
    """Test risk analysis with real house_platform data."""
    db = SessionLocal()
    repository = HouseBldrgstRepository()

    try:
        # Fetch first 5 properties from house_platform
        properties = db.query(HousePlatformORM).limit(5).all()

        if not properties:
            logger.error("No properties found in house_platform table")
            return

        logger.info("=" * 80)
        logger.info("RISK ANALYSIS TEST WITH REAL HOUSE_PLATFORM DATA")
        logger.info("=" * 80)
        logger.info(f"Testing with {len(properties)} properties\n")

        for idx, prop in enumerate(properties, start=1):
            logger.info(f"[{idx}/{len(properties)}] Processing property:")
            logger.info(f"  house_platform_id: {prop.house_platform_id}")
            logger.info(f"  address: {prop.address}")

            try:
                # Create risk score from real data
                risk_score = create_risk_score_from_data(
                    house_platform_id=prop.house_platform_id,
                    address=prop.address or "Unknown Address"
                )

                logger.info(f"  Risk Analysis Result:")
                logger.info(f"    Total Score: {risk_score.total_score}")
                logger.info(f"    Risk Level: {risk_score.risk_level}")
                logger.info(f"    Violations: {risk_score.violation_risk}")
                logger.info(f"    Seismic: {risk_score.seismic_risk}")
                logger.info(f"    Age: {risk_score.age_risk}")
                logger.info(f"    Price Deviation: {risk_score.price_deviation_risk}")
                logger.info(f"    Warnings: {risk_score.warnings}")

                # Save to house_bldrgst table
                saved_record = repository.save(
                    db=db,
                    risk_score=risk_score,
                    address=prop.address or "Unknown Address"
                )

                logger.info(f"  Saved to DB:")
                logger.info(f"    house_bldrgst_id: {saved_record.house_bldrgst_id}")
                logger.info(f"    house_platform_id: {saved_record.house_platform_id}")
                logger.info(f"    total_score: {saved_record.total_score}")

                # Verify saved record
                verified = repository.find_by_house_platform_id(db, prop.house_platform_id)
                if verified:
                    logger.info(f"  ✓ Verification: Record found in house_bldrgst")
                else:
                    logger.warning(f"  ✗ Verification: Record NOT found")

                logger.info("")

            except Exception as e:
                logger.error(f"  ERROR: {e}")
                logger.info("")
                continue

        logger.info("=" * 80)
        logger.info("TEST COMPLETE")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)

    finally:
        db.close()


if __name__ == "__main__":
    main()
