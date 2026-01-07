"""
HouseBldrgstRepository UPSERT 기능 테스트
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.orm import Base
from infrastructure.orm.house_bldrgst_orm import HouseBldrgst
from modules.house_analysis.adapter.output.repository.house_bldrgst_repository import (
    HouseBldrgstRepository,
)


@pytest.fixture
def db_session():
    """테스트용 in-memory SQLite DB 세션"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_house_bldrgst_repository_upsert_insert(db_session):
    """
    house_bldrgst 테이블에 새 데이터 INSERT 테스트

    Given: 빈 DB와 PNU 기반 건축물대장 데이터
    When: HouseBldrgstRepository.upsert() 호출
    Then: 데이터가 INSERT되고 조회 가능
    """
    # Given
    repo = HouseBldrgstRepository(db_session)
    pnu_id = "1168010100107770000"
    bldrgst_data = {
        "violation_yn": "N",
        "main_use_name": "아파트",
        "approval_date": "20100315",
        "seismic_yn": "Y",
    }

    # When
    repo.upsert(pnu_id, bldrgst_data)
    db_session.commit()

    # Then
    result = db_session.query(HouseBldrgst).filter_by(pnu_id=pnu_id).first()
    assert result is not None
    assert result.pnu_id == pnu_id
    assert result.violation_yn == "N"
    assert result.main_use_name == "아파트"
    assert result.approval_date == "20100315"
    assert result.seismic_yn == "Y"


def test_house_bldrgst_repository_upsert_update(db_session):
    """
    이미 존재하는 PNU에 대해 UPDATE 테스트

    Given: 이미 존재하는 PNU 데이터
    When: 동일 PNU로 다른 데이터를 upsert() 호출
    Then: 기존 데이터가 UPDATE됨
    """
    # Given - 기존 데이터 삽입
    repo = HouseBldrgstRepository(db_session)
    pnu_id = "1168010100107770000"
    old_data = {
        "violation_yn": "N",
        "main_use_name": "아파트",
        "approval_date": "20100315",
        "seismic_yn": "Y",
    }
    repo.upsert(pnu_id, old_data)
    db_session.commit()

    # When - 동일 PNU에 새 데이터 UPSERT
    new_data = {
        "violation_yn": "Y",  # 변경됨
        "main_use_name": "다세대주택",  # 변경됨
        "approval_date": "20050101",  # 변경됨
        "seismic_yn": "N",  # 변경됨
    }
    repo.upsert(pnu_id, new_data)
    db_session.commit()

    # Then - 데이터가 업데이트되었는지 확인
    result = db_session.query(HouseBldrgst).filter_by(pnu_id=pnu_id).first()
    assert result is not None
    assert result.violation_yn == "Y"
    assert result.main_use_name == "다세대주택"
    assert result.approval_date == "20050101"
    assert result.seismic_yn == "N"

    # 단 하나의 레코드만 존재해야 함
    count = db_session.query(HouseBldrgst).filter_by(pnu_id=pnu_id).count()
    assert count == 1


def test_house_bldrgst_repository_upsert_partial_data(db_session):
    """
    일부 필드만 제공된 경우에도 UPSERT 가능한지 테스트

    Given: 일부 필드만 포함된 데이터
    When: upsert() 호출
    Then: 제공된 필드만 저장되고, 나머지는 NULL
    """
    # Given
    repo = HouseBldrgstRepository(db_session)
    pnu_id = "1168010100205550000"
    partial_data = {
        "violation_yn": "N",
        "main_use_name": "다가구주택",
        # approval_date, seismic_yn 없음
    }

    # When
    repo.upsert(pnu_id, partial_data)
    db_session.commit()

    # Then
    result = db_session.query(HouseBldrgst).filter_by(pnu_id=pnu_id).first()
    assert result is not None
    assert result.violation_yn == "N"
    assert result.main_use_name == "다가구주택"
    assert result.approval_date is None
    assert result.seismic_yn is None
