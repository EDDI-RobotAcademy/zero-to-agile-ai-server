from typing import Dict, Any


def parse_pnu(pnu_id: str) -> Dict[str, str]:
    """
    PNU(필지번호) 19자리를 법정동코드, 본번, 지번으로 파싱

    PNU 구조 (19자리):
    - 법정동코드 (10자리)
    - 대지구분 (1자리): 1=대지, 2=산 (무시)
    - 본번 (4자리): 0000~9999
    - 부번 (4자리): 0000~9999

    Args:
        pnu_id: 19자리 PNU 문자열

    Returns:
        Dict containing:
        - legal_code: 법정동코드 (10자리)
        - bun: 본번 (앞의 0 제거)
        - ji: 부번 (앞의 0 제거, 0000이면 "0")

    Raises:
        ValueError: PNU ID가 19자리가 아닌 경우
    """
    if len(pnu_id) != 19:
        raise ValueError("PNU ID는 19자리여야 합니다")

    # 법정동코드 (0~9)
    legal_code = pnu_id[0:10]

    # 대지구분 (10) - 무시

    # 본번 (11~14)
    bun_raw = pnu_id[11:15]
    bun = str(int(bun_raw))  # 앞의 0 제거

    # 부번 (15~18)
    ji_raw = pnu_id[15:19]
    ji = str(int(ji_raw))  # 앞의 0 제거

    return {
        "legal_code": legal_code,
        "bun": bun,
        "ji": ji,
    }


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

    # 위반 건축물 여부 (최대 45점)
    if building_info.get("is_violation", False):
        score += 45

    # 내진 설계 적용 여부 (미적용/정보없음: +10)
    has_seismic_design = building_info.get("has_seismic_design")
    if has_seismic_design is not True:
        score += 10

    # 노후도 (최대 20점, 5구간)
    building_age = building_info.get("building_age", 0)
    if building_age <= 5:
        score += 0
    elif building_age <= 9:
        score += 4
    elif building_age <= 19:
        score += 8
    elif building_age <= 29:
        score += 14
    else:
        score += 20

    # 주용도코드명 (최대 25점)
    main_use = str(building_info.get("main_use", "")).strip()
    main_use_score = {
        # 안전
        "단독주택": 0,
        "다가구주택": 0,
        "다세대주택": 0,
        "아파트": 0,
        # 주의
        "오피스텔": 8,
        # 위험
        "다중주택": 18,
        "근린생활시설": 18,
        "고시원": 18,
        "업무시설": 18,
        # 매우 위험
        "생활형숙박시설": 25,
        "창고": 25,
        "공장": 25,
    }.get(main_use, 0)
    score += main_use_score

    return score


def generate_risk_summary(score: int) -> int:
    """
    리스크 점수에 따른 요약 메시지 생성

    Args:
        score: 리스크 점수

    Returns:
        위험 등급 (int)
    """
    if score <= 19:
        return 1
    elif score <= 39:
        return 2
    elif score <= 59:
        return 3
    elif score <= 79:
        return 4
    else:
        return 5


def generate_risk_comment(building_info: Dict[str, Any]) -> str:
    """
    리스크 요인을 간략 코멘트로 요약

    Args:
        building_info: 건축물 정보 딕셔너리

    Returns:
        요약 코멘트 (str)
    """
    reasons = []

    if building_info.get("is_violation", False):
        reasons.append("위반 건축물")

    if building_info.get("has_seismic_design") is not True:
        reasons.append("내진 설계 미적용")

    building_age = building_info.get("building_age", 0)
    if building_age >= 30:
        reasons.append("30년 이상 노후")
    elif building_age >= 20:
        reasons.append("20년 이상 노후")
    elif building_age >= 10:
        reasons.append("10년 이상 노후")

    main_use = str(building_info.get("main_use", "")).strip()
    risky_uses = {
        "오피스텔",
        "다중주택",
        "근린생활시설",
        "고시원",
        "업무시설",
        "생활형숙박시설",
        "창고",
        "공장",
    }
    if main_use in risky_uses:
        reasons.append(f"주용도: {main_use}")

    if not reasons:
        return "큰 위험 요인 없음"

    return ", ".join(reasons)


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
