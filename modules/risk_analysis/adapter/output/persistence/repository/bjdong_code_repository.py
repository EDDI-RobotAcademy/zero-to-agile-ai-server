"""
Repository for querying legal dong codes.

This repository provides data access methods for the bjdong_cd_mgm table,
which contains Korean legal dong codes used for government API queries.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from modules.risk_analysis.adapter.output.persistence.orm.bjdong_code_orm import BjdongCodeORM


class BjdongCodeRepository:
    """Repository for querying legal dong codes."""

    def find_by_address_components(
        self,
        db: Session,
        sido: str,
        sigungu: str,
        dong: str
    ) -> Optional[BjdongCodeORM]:
        """
        Find legal dong code by address components.

        Args:
            db: SQLAlchemy session
            sido: Sido name (supports variations like "서울시" or "서울특별시")
            sigungu: Sigungu name (e.g., "강남구")
            dong: Legal dong name (e.g., "역삼동")

        Returns:
            BjdongCodeORM if found, None otherwise
        """
        # Handle sido name variations
        sido_variations = self._generate_sido_variations(sido)

        # Query with multiple sido variations
        query = db.query(BjdongCodeORM).filter(
            or_(*[BjdongCodeORM.sido_nm == var for var in sido_variations]),
            BjdongCodeORM.sigungu_nm == sigungu,
            BjdongCodeORM.bjdong_nm == dong
        )

        result = query.first()

        # Mark as used if found
        if result:
            result.del_yn = "1"
            db.commit()

        return result

    def _generate_sido_variations(self, sido: str) -> list[str]:
        """
        Generate variations of sido name.

        Examples:
            "서울시" -> ["서울시", "서울특별시"]
            "부산시" -> ["부산시", "부산광역시"]

        Args:
            sido: Sido name (e.g., "서울시")

        Returns:
            List of sido name variations
        """
        # Map short names to official names
        sido_map = {
            "서울시": "서울특별시",
            "부산시": "부산광역시",
            "대구시": "대구광역시",
            "인천시": "인천광역시",
            "광주시": "광주광역시",
            "대전시": "대전광역시",
            "울산시": "울산광역시",
            "세종시": "세종특별자치시",
        }

        variations = [sido]
        if sido in sido_map:
            variations.append(sido_map[sido])

        return variations
