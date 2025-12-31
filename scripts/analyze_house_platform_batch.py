"""
Batch analysis script for house_platform properties.

This script reads all properties from house_platform table,
analyzes risk for each property, and saves results to house_bldrgst table.

Usage:
    python -m scripts.analyze_house_platform_batch
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


def create_dummy_risk_score(house_platform_id: int, address: str) -> RiskScore:
    """
    Create a dummy risk score for testing.

    In production, this would call real API services to fetch building
    and transaction data, then calculate actual risk scores.

    Args:
        house_platform_id: ID from house_platform table
        address: Full address from house_platform table

    Returns:
        RiskScore with dummy values
    """
    # For now, create a dummy risk score
    # TODO: Replace with actual API calls and risk calculation
    return RiskScore(
        house_platform_id=f"PROP-{house_platform_id:03d}",
        total_score=50.0,  # Dummy score
        violation_risk=10.0,
        price_deviation_risk=15.0,
        seismic_risk=15.0,
        age_risk=10.0,
        risk_level="MEDIUM",
        warnings=["Dummy analysis - replace with real implementation"]
    )


def main():
    """Analyze all house_platform properties and save to house_bldrgst."""
    db = SessionLocal()
    repository = HouseBldrgstRepository()

    try:
        # Fetch all properties from house_platform
        properties = db.query(HousePlatformORM).all()
        total_count = len(properties)
        logger.info(f"Found {total_count} properties to analyze")

        if total_count == 0:
            logger.warning("No properties found in house_platform table")
            return

        success_count = 0
        error_count = 0

        for idx, prop in enumerate(properties, start=1):
            try:
                logger.info(f"[{idx}/{total_count}] Analyzing property {prop.house_platform_id}: {prop.address}")

                # Create dummy risk score
                # TODO: Replace with actual risk analysis
                risk_score = create_dummy_risk_score(
                    house_platform_id=prop.house_platform_id,
                    address=prop.address or "Unknown Address"
                )

                # Save to house_bldrgst table (UPSERT)
                saved_record = repository.save(
                    db=db,
                    risk_score=risk_score,
                    address=prop.address or "Unknown Address"
                )

                logger.info(
                    f"  SUCCESS: Saved house_platform_id={saved_record.house_platform_id}, "
                    f"total_score={saved_record.total_score}"
                )
                success_count += 1

            except Exception as e:
                logger.error(f"  ERROR: Failed to analyze property {prop.house_platform_id}: {e}")
                error_count += 1
                continue

        # Print summary
        logger.info("=" * 80)
        logger.info("BATCH ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total properties: {total_count}")
        logger.info(f"Successfully analyzed: {success_count}")
        logger.info(f"Failed: {error_count}")
        logger.info(f"Success rate: {success_count / total_count * 100:.1f}%")

    finally:
        db.close()


if __name__ == "__main__":
    main()
