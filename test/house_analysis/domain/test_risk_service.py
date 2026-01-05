import pytest
from modules.house_analysis.domain.model import RiskScore
from modules.house_analysis.domain.service import calculate_risk_score, generate_risk_summary


def test_risk_score_domain_model_creation():
    """
    RiskScore 도메인 모델 생성 테스트
    - score, factors, summary 필드를 가진 dataclass
    - 기본값 설정 확인
    """
    # Given: 리스크 점수 데이터
    score = 72
    factors = {"violation": True, "seismic_design": False, "building_age": 30}
    summary = "내진 설계 미적용, 준공 30년 이상으로 위험도 높음"

    # When: RiskScore 도메인 모델 생성
    risk_score = RiskScore(score=score, factors=factors, summary=summary)

    # Then: 모델이 올바르게 생성되고 값이 저장됨
    assert risk_score.score == 72
    assert risk_score.factors == {"violation": True, "seismic_design": False, "building_age": 30}
    assert risk_score.summary == "내진 설계 미적용, 준공 30년 이상으로 위험도 높음"


def test_calculate_risk_score_with_violation():
    """
    위반 건축물인 경우 리스크 점수 계산 테스트
    - 위반 여부가 True이면 점수 +30
    """
    # Given: 위반 건축물 정보
    building_info = {
        "is_violation": True,
        "has_seismic_design": True,
        "building_age": 5
    }

    # When: 리스크 점수 계산
    score = calculate_risk_score(building_info)

    # Then: 위반 건축물이므로 점수가 30 이상이어야 함
    assert score >= 30
    assert score == 30  # 위반만 있으므로 정확히 30점


def test_calculate_risk_score_without_seismic_design():
    """
    내진 설계 없는 경우 리스크 점수 계산 테스트
    - 내진 설계가 False이면 점수 +25
    """
    # Given: 내진 설계가 없는 건축물 정보
    building_info = {
        "is_violation": False,
        "has_seismic_design": False,
        "building_age": 5
    }

    # When: 리스크 점수 계산
    score = calculate_risk_score(building_info)

    # Then: 내진 설계가 없으므로 점수가 25여야 함
    assert score == 25


def test_calculate_risk_score_by_building_age():
    """
    건물 노후도에 따른 리스크 점수 계산 테스트
    - 30년 이상: +40점
    - 20~30년: +30점
    - 10~20년: +20점
    - 10년 미만: +10점
    """
    # Given & When & Then: 30년 이상 건물
    building_info_30_plus = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 35
    }
    score_30_plus = calculate_risk_score(building_info_30_plus)
    assert score_30_plus == 40

    # Given & When & Then: 20~30년 건물
    building_info_20_to_30 = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 25
    }
    score_20_to_30 = calculate_risk_score(building_info_20_to_30)
    assert score_20_to_30 == 30

    # Given & When & Then: 10~20년 건물
    building_info_10_to_20 = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 15
    }
    score_10_to_20 = calculate_risk_score(building_info_10_to_20)
    assert score_10_to_20 == 20

    # Given & When & Then: 10년 미만 건물
    building_info_under_10 = {
        "is_violation": False,
        "has_seismic_design": True,
        "building_age": 5
    }
    score_under_10 = calculate_risk_score(building_info_under_10)
    assert score_under_10 == 10


def test_calculate_risk_score_combined():
    """
    여러 요소가 결합된 리스크 점수 계산 테스트
    - 위반 건축물 + 내진 미적용 + 30년 이상 = 30 + 25 + 40 = 95점
    """
    # Given: 모든 위험 요소를 가진 건축물
    building_info = {
        "is_violation": True,
        "has_seismic_design": False,
        "building_age": 35
    }

    # When: 리스크 점수 계산
    score = calculate_risk_score(building_info)

    # Then: 모든 요소가 합산되어 95점
    assert score == 95  # 30 (위반) + 25 (내진X) + 40 (30년 이상)


def test_generate_risk_summary_message():
    """
    리스크 점수에 따른 요약 메시지 생성 테스트
    - 점수 범위별 적절한 메시지 반환
    """
    # Given & When & Then: 낮은 위험 (0-30점)
    summary_low = generate_risk_summary(25)
    assert "낮음" in summary_low or "안전" in summary_low

    # Given & When & Then: 보통 위험 (31-60점)
    summary_medium = generate_risk_summary(45)
    assert "보통" in summary_medium or "주의" in summary_medium

    # Given & When & Then: 높은 위험 (61-80점)
    summary_high = generate_risk_summary(72)
    assert "높음" in summary_high or "위험" in summary_high

    # Given & When & Then: 매우 높은 위험 (81점 이상)
    summary_very_high = generate_risk_summary(95)
    assert "매우" in summary_very_high or "심각" in summary_very_high
