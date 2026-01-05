from typing import Dict, Any


def calculate_risk_score(building_info: Dict[str, Any]) -> int:
    """
    건축물 정보를 받아 리스크 점수를 계산하는 순수 도메인 로직

    Args:
        building_info: 건축물 정보 딕셔너리
            - is_violation: 위반 건축물 여부
            - has_seismic_design: 내진 설계 여부
            - building_age: 건물 연령

    Returns:
        리스크 점수 (int)
    """
    score = 0

    # 위반 건축물인 경우 +30점
    if building_info.get("is_violation", False):
        score += 30

    # 내진 설계가 없는 경우 +25점
    if not building_info.get("has_seismic_design", True):
        score += 25

    # 건물 노후도에 따른 점수 계산
    building_age = building_info.get("building_age", 0)
    if building_age >= 30:
        score += 40
    elif building_age >= 20:
        score += 30
    elif building_age >= 10:
        score += 20
    else:
        score += 10

    return score


def generate_risk_summary(score: int) -> str:
    """
    리스크 점수에 따른 요약 메시지 생성

    Args:
        score: 리스크 점수

    Returns:
        요약 메시지 (str)
    """
    if score <= 30:
        return "위험도 낮음"
    elif score <= 60:
        return "위험도 보통"
    elif score <= 80:
        return "위험도 높음"
    else:
        return "위험도 매우 높음"


def calculate_price_per_area(price: float, area: float) -> float:
    """
    3.3㎡당 가격 계산 (평당 가격)

    Args:
        price: 전세가 또는 매매가
        area: 전용면적 (㎡)

    Returns:
        평당 가격 (float)
    """
    return (price / area) * 3.3


def calculate_price_score(price_per_area: float, area_average: float) -> int:
    """
    지역 평균 대비 가격 적정성 점수 계산

    Args:
        price_per_area: 해당 매물의 평당 가격
        area_average: 지역 평균 평당 가격

    Returns:
        가격 점수 (int)
        - 높을수록 좋음 (가격이 낮을수록 점수 높음)
        - 낮을수록 나쁨 (가격이 높을수록 점수 낮음)
    """
    # 평균 대비 차이 비율 계산
    diff_percent = ((price_per_area - area_average) / area_average) * 100

    # 평균보다 높으면 점수 낮음, 낮으면 점수 높음
    # 기준점: 평균 = 50점
    # 10% 차이당 약 5점 변동
    score = 50 - int(diff_percent * 0.5)

    return score


def generate_price_comment(price_per_area: float, area_average: float) -> str:
    """
    가격 점수에 따른 코멘트 생성

    Args:
        price_per_area: 해당 매물의 평당 가격
        area_average: 지역 평균 평당 가격

    Returns:
        코멘트 (str)
    """
    # 평균 대비 차이 비율 계산
    diff_percent = ((price_per_area - area_average) / area_average) * 100

    if abs(diff_percent) < 1:
        return "동 평균과 비슷한 가격"
    elif diff_percent > 0:
        return f"동 평균 대비 약 {abs(int(diff_percent))}% 높은 가격"
    else:
        return f"동 평균 대비 약 {abs(int(diff_percent))}% 낮은 가격"
