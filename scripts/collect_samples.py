"""
Sample Data Collection Script for Risk Analysis.

This script collects 50 sample property risk analyses from various
Seoul districts and saves them to JSON format for use in RAG and LLM prompts.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from modules.risk_analysis.application.service.risk_service import RiskAnalysisService
from modules.risk_analysis.domain.model import BuildingInfo, TransactionInfo, RiskScore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Sample property data (50 properties from various Seoul districts)
SAMPLE_PROPERTIES = [
    # Mapo-gu (15 samples)
    {"address": "서울특별시 마포구 연남동 123-45", "approval_date": "20200115", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 52000, "area": 84.5},
    {"address": "서울특별시 마포구 서교동 234-56", "approval_date": "20150320", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 58000, "area": 92.3},
    {"address": "서울특별시 마포구 상수동 345-67", "approval_date": "20100810", "seismic": False, "violation": "정상", "structure": "철골조", "price": 48000, "area": 75.2},
    {"address": "서울특별시 마포구 망원동 456-78", "approval_date": "19951205", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 42000, "area": 68.9},
    {"address": "서울특별시 마포구 공덕동 567-89", "approval_date": "20180922", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 65000, "area": 102.1},
    {"address": "서울특별시 마포구 아현동 678-90", "approval_date": "20080415", "seismic": False, "violation": "정상", "structure": "철골조", "price": 45000, "area": 79.6},
    {"address": "서울특별시 마포구 대흥동 789-01", "approval_date": "20220510", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 72000, "area": 115.3},
    {"address": "서울특별시 마포구 도화동 890-12", "approval_date": "19880623", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 38000, "area": 62.4},
    {"address": "서울특별시 마포구 마포동 901-23", "approval_date": "20130718", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 55000, "area": 88.7},
    {"address": "서울특별시 마포구 토정동 012-34", "approval_date": "20050930", "seismic": False, "violation": "정상", "structure": "철골조", "price": 43000, "area": 72.8},
    {"address": "서울특별시 마포구 신수동 123-56", "approval_date": "20191104", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 61000, "area": 95.5},
    {"address": "서울특별시 마포구 현석동 234-67", "approval_date": "19921215", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 36000, "area": 58.3},
    {"address": "서울특별시 마포구 구수동 345-78", "approval_date": "20160308", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 57000, "area": 90.1},
    {"address": "서울특별시 마포구 노고산동 456-89", "approval_date": "20030522", "seismic": False, "violation": "정상", "structure": "철골조", "price": 44000, "area": 76.9},
    {"address": "서울특별시 마포구 창전동 567-90", "approval_date": "20210626", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 68000, "area": 108.2},

    # Yongsan-gu (15 samples)
    {"address": "서울특별시 용산구 이태원동 100-1", "approval_date": "20170415", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 82000, "area": 125.3},
    {"address": "서울특별시 용산구 한남동 200-2", "approval_date": "19981012", "seismic": False, "violation": "정상", "structure": "철골조", "price": 95000, "area": 145.7},
    {"address": "서울특별시 용산구 서빙고동 300-3", "approval_date": "20120720", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 78000, "area": 118.4},
    {"address": "서울특별시 용산구 보광동 400-4", "approval_date": "19891205", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 62000, "area": 95.2},
    {"address": "서울특별시 용산구 용산동 500-5", "approval_date": "20190308", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 88000, "area": 135.6},
    {"address": "서울특별시 용산구 남영동 600-6", "approval_date": "20060515", "seismic": False, "violation": "정상", "structure": "철골조", "price": 66000, "area": 102.3},
    {"address": "서울특별시 용산구 청파동 700-7", "approval_date": "20200922", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 92000, "area": 142.1},
    {"address": "서울특별시 용산구 원효로동 800-8", "approval_date": "19941118", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 58000, "area": 88.9},
    {"address": "서울특별시 용산구 효창동 900-9", "approval_date": "20140625", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 75000, "area": 112.5},
    {"address": "서울특별시 용산구 도원동 101-10", "approval_date": "20010830", "seismic": False, "violation": "정상", "structure": "철골조", "price": 64000, "area": 98.7},
    {"address": "서울특별시 용산구 문배동 202-11", "approval_date": "20180704", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 85000, "area": 130.2},
    {"address": "서울특별시 용산구 신계동 303-12", "approval_date": "19961015", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 60000, "area": 92.1},
    {"address": "서울특별시 용산구 한강로동 404-13", "approval_date": "20150210", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 79000, "area": 120.8},
    {"address": "서울특별시 용산구 이촌동 505-14", "approval_date": "20040920", "seismic": False, "violation": "정상", "structure": "철골조", "price": 67000, "area": 104.5},
    {"address": "서울특별시 용산구 동빙고동 606-15", "approval_date": "20210515", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 90000, "area": 138.3},

    # Yeongdeungpo-gu (10 samples)
    {"address": "서울특별시 영등포구 여의도동 50-1", "approval_date": "20160820", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 98000, "area": 152.4},
    {"address": "서울특별시 영등포구 당산동 51-2", "approval_date": "20070425", "seismic": False, "violation": "정상", "structure": "철골조", "price": 62000, "area": 96.8},
    {"address": "서울특별시 영등포구 영등포동 52-3", "approval_date": "19931108", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 48000, "area": 74.2},
    {"address": "서울특별시 영등포구 신길동 53-4", "approval_date": "20190612", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 75000, "area": 115.6},
    {"address": "서울특별시 영등포구 대림동 54-5", "approval_date": "20020315", "seismic": False, "violation": "정상", "structure": "철골조", "price": 55000, "area": 85.3},
    {"address": "서울특별시 영등포구 도림동 55-6", "approval_date": "20210720", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 82000, "area": 126.9},
    {"address": "서울특별시 영등포구 문래동 56-7", "approval_date": "19990530", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 52000, "area": 80.7},
    {"address": "서울특별시 영등포구 양평동 57-8", "approval_date": "20130925", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 68000, "area": 105.4},
    {"address": "서울특별시 영등포구 양화동 58-9", "approval_date": "20050810", "seismic": False, "violation": "정상", "structure": "철골조", "price": 59000, "area": 91.2},
    {"address": "서울특별시 영등포구 선유동 59-10", "approval_date": "20200105", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 78000, "area": 120.5},

    # Other districts (10 samples)
    {"address": "서울특별시 강남구 역삼동 10-1", "approval_date": "20180315", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 120000, "area": 185.3},
    {"address": "서울특별시 서초구 서초동 11-2", "approval_date": "20110620", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 105000, "area": 162.7},
    {"address": "서울특별시 송파구 잠실동 12-3", "approval_date": "20030815", "seismic": False, "violation": "정상", "structure": "철골조", "price": 88000, "area": 136.5},
    {"address": "서울특별시 강동구 천호동 13-4", "approval_date": "19970925", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 62000, "area": 96.2},
    {"address": "서울특별시 광진구 자양동 14-5", "approval_date": "20160510", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 78000, "area": 120.8},
    {"address": "서울특별시 성동구 성수동 15-6", "approval_date": "20080120", "seismic": False, "violation": "정상", "structure": "철골조", "price": 72000, "area": 111.4},
    {"address": "서울특별시 종로구 삼청동 16-7", "approval_date": "20210405", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 115000, "area": 178.2},
    {"address": "서울특별시 중구 명동 17-8", "approval_date": "19920710", "seismic": False, "violation": "위반", "structure": "벽돌조", "price": 65000, "area": 100.5},
    {"address": "서울특별시 동작구 사당동 18-9", "approval_date": "20140830", "seismic": True, "violation": "정상", "structure": "철근콘크리트구조", "price": 68000, "area": 105.3},
    {"address": "서울특별시 관악구 신림동 19-10", "approval_date": "20000615", "seismic": False, "violation": "정상", "structure": "철골조", "price": 54000, "area": 83.7},
]


def create_historical_transactions(base_price: int, area: float) -> List[TransactionInfo]:
    """
    Create sample historical transactions around the base price.

    Args:
        base_price: Base price for the property
        area: Property area

    Returns:
        List of 3 historical transactions
    """
    return [
        TransactionInfo(
            address="서울특별시 동일지역",
            transaction_date="2024-09-01",
            price=int(base_price * 0.96),  # -4%
            area=area
        ),
        TransactionInfo(
            address="서울특별시 동일지역",
            transaction_date="2024-10-01",
            price=base_price,  # same
            area=area
        ),
        TransactionInfo(
            address="서울특별시 동일지역",
            transaction_date="2024-10-15",
            price=int(base_price * 1.04),  # +4%
            area=area
        ),
    ]


def risk_score_to_dict(risk_score: RiskScore) -> Dict:
    """
    Convert RiskScore to dictionary for JSON serialization.

    Args:
        risk_score: RiskScore object

    Returns:
        Dictionary representation
    """
    return {
        "house_platform_id": risk_score.house_platform_id,
        "total_score": risk_score.total_score,
        "violation_risk": risk_score.violation_risk,
        "price_deviation_risk": risk_score.price_deviation_risk,
        "seismic_risk": risk_score.seismic_risk,
        "age_risk": risk_score.age_risk,
        "risk_level": risk_score.risk_level,
        "warnings": risk_score.warnings
    }


def collect_samples():
    """Collect 50 sample property risk analyses."""
    logger.info("Starting sample data collection...")

    # Initialize service
    service = RiskAnalysisService()

    # Collect results
    results = []
    success_count = 0
    fail_count = 0

    for idx, prop_data in enumerate(SAMPLE_PROPERTIES, start=1):
        house_platform_id = f"PROP-{idx:03d}"

        try:
            # Create building info
            building = BuildingInfo(
                address=prop_data["address"],
                approval_date=prop_data["approval_date"],
                seismic_design=prop_data["seismic"],
                violation_status=prop_data["violation"],
                structure_type=prop_data["structure"]
            )

            # Create current transaction
            transaction = TransactionInfo(
                address=prop_data["address"],
                transaction_date="2024-11-15",
                price=prop_data["price"],
                area=prop_data["area"]
            )

            # Create historical transactions
            historical = create_historical_transactions(prop_data["price"], prop_data["area"])

            # Analyze risk
            risk_score = service.analyze_property(
                building=building,
                transaction=transaction,
                house_platform_id=house_platform_id,
                historical_transactions=historical
            )

            # Add to results with address
            result_dict = risk_score_to_dict(risk_score)
            result_dict["address"] = prop_data["address"]
            results.append(result_dict)

            success_count += 1
            logger.info(f"✓ {house_platform_id}: {prop_data['address']} - {risk_score.risk_level} ({risk_score.total_score:.1f})")

        except Exception as e:
            fail_count += 1
            logger.error(f"✗ {house_platform_id}: {prop_data['address']} - Error: {str(e)}")

    logger.info(f"\nCollection complete: {success_count} succeeded, {fail_count} failed")

    return results


def save_samples(samples: List[Dict], output_path: Path):
    """
    Save samples to JSON file.

    Args:
        samples: List of sample dictionaries
        output_path: Path to output JSON file
    """
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(samples)} samples to {output_path}")


def print_statistics(samples: List[Dict]):
    """Print statistics about collected samples."""
    total = len(samples)
    low_count = sum(1 for s in samples if s["risk_level"] == "LOW")
    medium_count = sum(1 for s in samples if s["risk_level"] == "MEDIUM")
    high_count = sum(1 for s in samples if s["risk_level"] == "HIGH")
    avg_score = sum(s["total_score"] for s in samples) / total if total > 0 else 0

    logger.info("\n=== Sample Statistics ===")
    logger.info(f"Total samples: {total}")
    logger.info(f"LOW risk: {low_count} ({low_count/total*100:.1f}%)")
    logger.info(f"MEDIUM risk: {medium_count} ({medium_count/total*100:.1f}%)")
    logger.info(f"HIGH risk: {high_count} ({high_count/total*100:.1f}%)")
    logger.info(f"Average score: {avg_score:.1f}")


def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("Risk Analysis Sample Data Collection")
    logger.info("="*60)

    # Collect samples
    samples = collect_samples()

    # Save to file
    output_path = Path("data/samples/risk_samples.json")
    save_samples(samples, output_path)

    # Print statistics
    print_statistics(samples)

    logger.info("\n" + "="*60)
    logger.info("Sample collection complete!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
