"""
Tests for HouseBldrgstORM model.

This test module validates the SQLAlchemy ORM mapping to the house_bldrgst table.
"""

import pytest
from modules.risk_analysis.adapter.output.persistence.orm.house_bldrgst_orm import HouseBldrgstORM


class TestHouseBldrgstORM:
    """Test suite for HouseBldrgstORM model."""

    def test_orm_can_be_imported(self):
        """Test that HouseBldrgstORM can be imported successfully."""
        assert HouseBldrgstORM is not None

    def test_orm_has_correct_tablename(self):
        """Test that ORM maps to correct table name."""
        assert HouseBldrgstORM.__tablename__ == "house_bldrgst"

    def test_orm_can_be_instantiated_with_required_fields(self):
        """Test that HouseBldrgstORM can be instantiated with required fields."""
        bldrgst = HouseBldrgstORM(
            house_platform_id=1,
            address="서울특별시 강남구 역삼동 777-88",
            total_score=45
        )

        assert bldrgst.house_platform_id == 1
        assert bldrgst.address == "서울특별시 강남구 역삼동 777-88"
        assert bldrgst.total_score == 45

    def test_orm_can_be_instantiated_with_minimal_fields(self):
        """Test that HouseBldrgstORM can be instantiated with minimal fields."""
        bldrgst = HouseBldrgstORM(
            house_platform_id=2
        )

        assert bldrgst.house_platform_id == 2
        assert bldrgst.address is None
        assert bldrgst.total_score is None

    def test_orm_has_autoincrement_primary_key(self):
        """Test that house_bldrgst_id is autoincrement primary key."""
        bldrgst = HouseBldrgstORM(
            house_platform_id=3,
            address="서울특별시 종로구 효자동 123",
            total_score=30
        )

        # Primary key should be None before insert (auto-generated)
        assert bldrgst.house_bldrgst_id is None
