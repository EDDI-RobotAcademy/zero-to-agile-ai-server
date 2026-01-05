import pytest
from modules.house_analysis.domain.model import PriceScore
from modules.house_analysis.domain.service import (
    calculate_price_per_area,
    calculate_price_score,
    generate_price_comment
)


def test_price_score_domain_model_creation():
    """
    PriceScore 도메인 모델 생성 테스트
    - score, comment, metrics 필드를 가진 dataclass
    """
    # Given: 가격 점수 데이터
    score = 38
    comment = "동 평균 대비 약 22% 높은 가격"
    metrics = {
        "price_per_area": 1200,
        "area_average": 983,
        "diff_percent": 22
    }

    # When: PriceScore 도메인 모델 생성
    price_score = PriceScore(score=score, comment=comment, metrics=metrics)

    # Then: 모델이 올바르게 생성되고 값이 저장됨
    assert price_score.score == 38
    assert price_score.comment == "동 평균 대비 약 22% 높은 가격"
    assert price_score.metrics == {
        "price_per_area": 1200,
        "area_average": 983,
        "diff_percent": 22
    }


def test_calculate_price_per_area():
    """
    3.3㎡당 가격 계산 테스트
    - 전세가 / 면적 * 3.3 = 평당 가격
    """
    # Given: 전세가와 면적 정보
    price = 50000000  # 5천만원
    area = 33.0  # 33㎡ (약 10평)

    # When: 3.3㎡당 가격 계산
    price_per_area = calculate_price_per_area(price, area)

    # Then: 평당 가격이 정확히 계산됨
    # 50,000,000 / 33 * 3.3 = 5,000,000 (평당 500만원)
    assert price_per_area == 5000000

    # Given: 다른 예시 - 전세가 1억, 면적 66㎡
    price2 = 100000000
    area2 = 66.0

    # When: 평당 가격 계산
    price_per_area2 = calculate_price_per_area(price2, area2)

    # Then: 100,000,000 / 66 * 3.3 = 5,000,000
    assert price_per_area2 == 5000000


def test_calculate_price_score_above_average():
    """
    지역 평균 대비 높은 가격 점수 계산 테스트
    - 평균 대비 +20% → 점수 40 (낮음)
    - 가격이 높을수록 점수가 낮음 (좋지 않음)
    """
    # Given: 평당 가격과 지역 평균
    price_per_area = 1200  # 평당 1200만원
    area_average = 1000  # 지역 평균 평당 1000만원
    # 차이: +20%

    # When: 가격 점수 계산
    score = calculate_price_score(price_per_area, area_average)

    # Then: 평균 대비 20% 높으므로 점수 40 (낮음)
    assert score == 40


def test_calculate_price_score_below_average():
    """
    지역 평균 대비 낮은 가격 점수 계산 테스트
    - 평균 대비 -10% → 점수 55 (보통)
    - 가격이 낮을수록 점수가 높음 (좋음)
    """
    # Given: 평당 가격과 지역 평균
    price_per_area = 900  # 평당 900만원
    area_average = 1000  # 지역 평균 평당 1000만원
    # 차이: -10%

    # When: 가격 점수 계산
    score = calculate_price_score(price_per_area, area_average)

    # Then: 평균 대비 10% 낮으므로 점수 55 (보통, 좋음)
    # 50 - (-10 * 0.5) = 50 + 5 = 55
    assert score == 55


def test_calculate_price_score_at_average():
    """
    지역 평균과 동일한 가격 점수 계산 테스트
    - 평균과 동일 → 점수 50 (기준점)
    """
    # Given: 평당 가격과 지역 평균이 동일
    price_per_area = 1000  # 평당 1000만원
    area_average = 1000  # 지역 평균 평당 1000만원
    # 차이: 0%

    # When: 가격 점수 계산
    score = calculate_price_score(price_per_area, area_average)

    # Then: 평균과 동일하므로 점수 50 (기준점)
    # 50 - (0 * 0.5) = 50
    assert score == 50


def test_generate_price_comment():
    """
    가격 점수에 따른 코멘트 생성 테스트
    - 평균 대비 퍼센트 차이를 포함한 코멘트 생성
    """
    # Given & When & Then: 평균 대비 22% 높은 경우
    comment_above = generate_price_comment(1200, 983)
    assert "22%" in comment_above
    assert "높은" in comment_above

    # Given & When & Then: 평균 대비 10% 낮은 경우
    comment_below = generate_price_comment(900, 1000)
    assert "10%" in comment_below
    assert "낮은" in comment_below

    # Given & When & Then: 평균과 동일한 경우
    comment_equal = generate_price_comment(1000, 1000)
    assert "평균" in comment_equal or "동일" in comment_equal
