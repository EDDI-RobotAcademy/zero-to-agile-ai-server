"""
Service to parse Korean addresses and retrieve legal dong codes.

This service is used to prepare parameters for Building Ledger API calls.
"""

from typing import Dict, Optional
import re
from sqlalchemy.orm import Session
from modules.risk_analysis.adapter.output.persistence.repository.bjdong_code_repository import BjdongCodeRepository


class AddressParsingError(Exception):
    """Exception raised when address parsing fails."""
    pass


class BjdongCodeNotFoundError(Exception):
    """Exception raised when bjdong code is not found in database."""
    pass


class AddressParserService:
    """
    Service to parse Korean addresses and retrieve legal dong codes.

    This service is used to prepare parameters for Building Ledger API calls.
    """

    def __init__(self, db: Session):
        """
        Initialize AddressParserService.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.repository = BjdongCodeRepository()

    def parse_address_and_get_codes(self, address: str) -> Dict[str, Optional[str]]:
        """
        Parse address string and retrieve legal dong codes.

        Args:
            address: Korean address string (e.g., "서울시 강남구 역삼동 777-88")

        Returns:
            Dictionary with keys:
                - sigungu_cd: 5-digit sigungu code
                - bjdong_cd: 5-digit bjdong code
                - bun: Main lot number (번)
                - ji: Sub lot number (지)

        Raises:
            AddressParsingError: If address format is invalid
            BjdongCodeNotFoundError: If legal dong code is not found in database
        """
        # Step 1: Parse address components
        components = self._parse_address_components(address)

        # Step 2: Query database for legal dong code
        bjdong_record = self.repository.find_by_address_components(
            db=self.db,
            sido=components["sido"],
            sigungu=components["sigungu"],
            dong=components["dong"]
        )

        if not bjdong_record:
            raise BjdongCodeNotFoundError(
                f"Legal dong code not found for: {components['sido']} {components['sigungu']} {components['dong']}"
            )

        # Step 3: Extract codes from full_cd
        full_cd = bjdong_record.full_cd
        if len(full_cd) != 10:
            raise ValueError(f"Invalid full_cd format: {full_cd} (expected 10 digits)")

        sigungu_cd = full_cd[:5]
        bjdong_cd = full_cd[5:]

        # Step 4: Return structured result
        return {
            "sigungu_cd": sigungu_cd,
            "bjdong_cd": bjdong_cd,
            "bun": components.get("bun"),
            "ji": components.get("ji"),
        }

    def _parse_address_components(self, address: str) -> Dict[str, Optional[str]]:
        """
        Parse address string into components.

        Args:
            address: Address string (e.g., "서울시 강남구 역삼동 777-88")

        Returns:
            Dictionary with sido, sigungu, dong, bun, ji

        Raises:
            AddressParsingError: If parsing fails
        """
        address = address.strip()

        if not address:
            raise AddressParsingError("Address cannot be empty")

        # Pattern: {sido} {sigungu} {dong} {bun}-{ji}
        # Pattern: {sido} {sigungu} {dong} {bun}
        # Pattern: {sido} {sigungu} {dong}
        # Supports: 동, 리, 가
        pattern = r"^(.+?)\s+(.+?[시군구])\s+(.+?[동리가])\s*(\d+)?(?:-(\d+))?$"

        match = re.match(pattern, address)
        if not match:
            raise AddressParsingError(f"Invalid address format: {address}")

        sido, sigungu, dong, bun, ji = match.groups()

        return {
            "sido": sido.strip(),
            "sigungu": sigungu.strip(),
            "dong": dong.strip(),
            "bun": bun.strip() if bun else None,
            "ji": ji.strip() if ji else None,
        }
