import pytest
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.orm.risk_score_history_orm import RiskScoreHistory
from infrastructure.orm.price_score_history_orm import PriceScoreHistory
from infrastructure.db.postgres import Base


def test_risk_score_history_orm_table_creation():
    """
    RiskScoreHistory ORM 모델 정의 테스트
    - 컬럼: id, address, risk_score, summary, factors(JSON), created_at
    """
    # When: ORM 모델의 컬럼 확인
    mapper = inspect(RiskScoreHistory)
    column_names = [column.key for column in mapper.columns]

    # Then: 필요한 컬럼이 모두 정의되어 있어야 함
    assert "id" in column_names
    assert "address" in column_names
    assert "risk_score" in column_names
    assert "summary" in column_names
    assert "factors" in column_names
    assert "created_at" in column_names

    # Then: 테이블명 확인
    assert RiskScoreHistory.__tablename__ == "risk_score_history"


def test_price_score_history_orm_table_creation():
    """
    PriceScoreHistory ORM 모델 정의 테스트
    - 컬럼: id, address, deal_type, price_score, comment, metrics(JSON), created_at
    """
    # When: ORM 모델의 컬럼 확인
    mapper = inspect(PriceScoreHistory)
    column_names = [column.key for column in mapper.columns]

    # Then: 필요한 컬럼이 모두 정의되어 있어야 함
    assert "id" in column_names
    assert "address" in column_names
    assert "deal_type" in column_names
    assert "price_score" in column_names
    assert "comment" in column_names
    assert "metrics" in column_names
    assert "created_at" in column_names

    # Then: 테이블명 확인
    assert PriceScoreHistory.__tablename__ == "price_score_history"


@pytest.fixture
def in_memory_db():
    """In-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_risk_score_history_save_and_load(in_memory_db):
    """
    RiskScoreHistory 저장 및 조회 테스트
    - DB에 데이터 저장 후 조회하여 검증
    """
    # Given: 리스크 점수 히스토리 데이터
    risk_history = RiskScoreHistory(
        address="서울시 강남구 역삼동 777",
        risk_score=72,
        summary="내진 설계 미적용, 준공 30년 이상으로 위험도 높음",
        factors={"violation": True, "seismic_design": False, "building_age": 30}
    )

    # When: DB에 저장
    in_memory_db.add(risk_history)
    in_memory_db.commit()

    # Then: 저장된 데이터를 조회하여 검증
    saved_history = in_memory_db.query(RiskScoreHistory).filter_by(
        address="서울시 강남구 역삼동 777"
    ).first()

    assert saved_history is not None
    assert saved_history.address == "서울시 강남구 역삼동 777"
    assert saved_history.risk_score == 72
    assert saved_history.summary == "내진 설계 미적용, 준공 30년 이상으로 위험도 높음"
    assert saved_history.factors["violation"] is True
    assert saved_history.factors["seismic_design"] is False
    assert saved_history.factors["building_age"] == 30
    assert saved_history.created_at is not None


def test_price_score_history_save_and_load(in_memory_db):
    """
    PriceScoreHistory 저장 및 조회 테스트
    - DB에 데이터 저장 후 조회하여 검증
    """
    # Given: 가격 점수 히스토리 데이터
    price_history = PriceScoreHistory(
        address="서울시 강남구 역삼동 777",
        deal_type="전세",
        price_score=38,
        comment="동 평균 대비 약 22% 높은 가격",
        metrics={"price_per_area": 1200, "area_average": 983, "diff_percent": 22}
    )

    # When: DB에 저장
    in_memory_db.add(price_history)
    in_memory_db.commit()

    # Then: 저장된 데이터를 조회하여 검증
    saved_history = in_memory_db.query(PriceScoreHistory).filter_by(
        address="서울시 강남구 역삼동 777"
    ).first()

    assert saved_history is not None
    assert saved_history.address == "서울시 강남구 역삼동 777"
    assert saved_history.deal_type == "전세"
    assert saved_history.price_score == 38
    assert saved_history.comment == "동 평균 대비 약 22% 높은 가격"
    assert saved_history.metrics["price_per_area"] == 1200
    assert saved_history.metrics["area_average"] == 983
    assert saved_history.metrics["diff_percent"] == 22
    assert saved_history.created_at is not None
