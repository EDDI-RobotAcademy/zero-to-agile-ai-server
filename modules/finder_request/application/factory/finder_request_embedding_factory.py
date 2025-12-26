from __future__ import annotations

from modules.finder_request.domain.finder_request import FinderRequest


def build_finder_request_embedding_text(request: FinderRequest) -> str:
    """요구서 임베딩에 사용할 텍스트를 생성한다."""
    if request.additional_condition:
        return request.additional_condition.strip()

    preferred = request.preferred_region or "지역 제한 없음"
    house_type = request.house_type or "주거 유형 제한 없음"
    price_type = request.price_type or "가격 유형 제한 없음"
    deposit = (
        f"보증금 {request.max_deposit}만원 이하"
        if request.max_deposit is not None
        else "보증금 제한 없음"
    )
    rent = (
        f"월세 {request.max_rent}만원 이하"
        if request.max_rent is not None
        else "월세 제한 없음"
    )
    return f"{preferred}, {house_type}, {price_type}, {deposit}, {rent}"
