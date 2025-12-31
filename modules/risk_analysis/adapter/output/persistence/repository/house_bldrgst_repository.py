"""
Repository for managing house_bldrgst table (Risk Analysis Results).

This repository provides data access methods for the house_bldrgst table,
including UPSERT (insert or update) support for risk analysis results.
"""

from typing import Optional
from sqlalchemy.orm import Session
from modules.risk_analysis.adapter.output.persistence.orm.house_bldrgst_orm import HouseBldrgstORM
from modules.risk_analysis.domain.model import RiskScore


class HouseBldrgstRepository:
    """Repository for managing house_bldrgst table (Risk Analysis Results)."""

    def save(
        self,
        db: Session,
        risk_score: RiskScore,
        address: str
    ) -> HouseBldrgstORM:
        """
        Save or update risk analysis result (UPSERT).

        Checks if a record with the given house_platform_id already exists.
        If it exists, updates it. Otherwise, creates a new record.

        Args:
            db: SQLAlchemy session
            risk_score: Calculated risk score object
            address: Full address of the property

        Returns:
            Saved/updated HouseBldrgstORM object

        Raises:
            ValueError: If house_platform_id is invalid
        """
        if not risk_score.house_platform_id:
            raise ValueError("house_platform_id cannot be empty")

        # Convert house_platform_id from string to integer for database
        house_platform_id_int = int(risk_score.house_platform_id.replace("PROP-", ""))

        # Check if a record with this house_platform_id already exists
        existing_record = self.find_by_house_platform_id(db, house_platform_id_int)

        if existing_record:
            # Update existing record
            existing_record.address = address
            existing_record.total_score = int(risk_score.total_score)
            db.commit()
            db.refresh(existing_record)
            return existing_record
        else:
            # Create new record
            new_record = HouseBldrgstORM(
                house_platform_id=house_platform_id_int,
                address=address,
                total_score=int(risk_score.total_score)
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            return new_record

    def find_by_house_platform_id(
        self,
        db: Session,
        house_platform_id: int
    ) -> Optional[HouseBldrgstORM]:
        """
        Find risk analysis result by house_platform_id.

        Args:
            db: SQLAlchemy session
            house_platform_id: Primary key (FK to house_platform table)

        Returns:
            HouseBldrgstORM if found, None otherwise
        """
        return db.query(HouseBldrgstORM).filter(
            HouseBldrgstORM.house_platform_id == house_platform_id
        ).first()
