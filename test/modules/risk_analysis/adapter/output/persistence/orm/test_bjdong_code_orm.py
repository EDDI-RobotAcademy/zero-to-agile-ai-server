"""
Tests for BjdongCodeORM model.

This test module validates the SQLAlchemy ORM mapping to the bjdong_cd_mgm table.
"""

import pytest
from modules.risk_analysis.adapter.output.persistence.orm.bjdong_code_orm import BjdongCodeORM


class TestBjdongCodeORM:
    """Test suite for BjdongCodeORM model."""

    def test_orm_can_be_imported(self):
        """Test that BjdongCodeORM can be imported successfully."""
        assert BjdongCodeORM is not None

    def test_orm_has_correct_tablename(self):
        """Test that ORM maps to correct table name."""
        assert BjdongCodeORM.__tablename__ == "bjdong_cd_mgm"

    def test_orm_can_be_instantiated(self):
        """Test that BjdongCodeORM can be instantiated with required fields."""
        bjdong = BjdongCodeORM(
            full_cd="1111010400",
            sido_nm="서울특별시",
            sigungu_nm="종로구",
            bjdong_nm="효자동",
            bjdong_full_nm="서울특별시 종로구 효자동",
            del_yn="0"
        )

        assert bjdong.full_cd == "1111010400"
        assert bjdong.sido_nm == "서울특별시"
        assert bjdong.sigungu_nm == "종로구"
        assert bjdong.bjdong_nm == "효자동"
        assert bjdong.bjdong_full_nm == "서울특별시 종로구 효자동"
        assert bjdong.del_yn == "0"
