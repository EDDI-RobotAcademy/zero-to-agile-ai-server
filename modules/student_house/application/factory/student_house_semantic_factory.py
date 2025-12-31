from __future__ import annotations

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseSemanticSource,
)


def build_student_house_description(source: StudentHouseSemanticSource) -> str:
    """대학생 관점에서 임베딩용 문장을 생성한다."""
    address = source.address or "주소 정보 없음"
    room_type = source.room_type or "방 형태 정보 없음"
    residence_type = source.residence_type or "주거 유형 정보 없음"

    floor_text = _format_floor(source.floor_no, source.all_floors)
    price_text = _format_price(
        source.deposit, source.monthly_rent, source.manage_cost
    )
    manage_text = _format_management(
        source.management_included, source.management_excluded
    )
    built_in_text = _format_list(source.built_in, "기본 옵션 정보 없음")
    elevator_text = "있음" if source.has_elevator else "없음"
    parking_text = "가능" if source.can_park else "불가"

    near_univ = _bool_to_text(source.near_univ, "학교 접근성 정보 없음")
    near_transport = _bool_to_text(
        source.near_transport, "대중교통 접근성 정보 없음"
    )
    near_mart = _bool_to_text(source.near_mart, "편의시설 접근성 정보 없음")

    risk_text = _format_risk(
        source.risk_score, source.risk_level, source.risk_reason
    )
    score_text = _format_score(source.base_total_score)

    description = f"""
[매물 개요]
이 매물은 {address}에 위치한 {residence_type} {room_type}입니다.
{floor_text}

[비용 정보]
{price_text}
{manage_text}

[옵션 및 편의시설]
기본 옵션: {built_in_text}
엘리베이터: {elevator_text}, 주차: {parking_text}
학교 접근성: {near_univ}
대중교통 접근성: {near_transport}
편의시설 접근성: {near_mart}

[리스크/추천 점수]
{risk_text}
{score_text}

[대학생 추천 포인트]
통학과 생활 편의성을 고려해 비용 대비 만족도를 평가했습니다.
{_format_student_note(source.near_univ, source.near_transport, source.near_mart)}
""".strip()

    return description


def _format_floor(floor_no: int | None, all_floors: int | None) -> str:
    if floor_no is None:
        return "층수 정보 없음"
    if all_floors:
        return f"전체 {all_floors}층 중 {floor_no}층"
    return f"{floor_no}층"


def _format_price(
    deposit: int | None, monthly_rent: int | None, manage_cost: int | None
) -> str:
    deposit_text = f"보증금 {deposit}만원" if deposit is not None else "보증금 정보 없음"
    rent_text = (
        f"월세 {monthly_rent}만원" if monthly_rent is not None else "월세 정보 없음"
    )
    manage_text = (
        f"관리비 {manage_cost}만원" if manage_cost is not None else "관리비 정보 없음"
    )
    return f"{deposit_text}, {rent_text}, {manage_text}"


def _format_management(
    included: list[str] | None, excluded: list[str] | None
) -> str:
    included_text = _format_list(included, "포함 항목 정보 없음")
    excluded_text = _format_list(excluded, "제외 항목 정보 없음")
    return f"관리비 포함: {included_text} / 제외: {excluded_text}"


def _format_list(values: list[str] | None, fallback: str) -> str:
    if not values:
        return fallback
    cleaned = [str(v).strip() for v in values if str(v).strip()]
    return ", ".join(cleaned) if cleaned else fallback


def _bool_to_text(value: bool | None, fallback: str) -> str:
    if value is None:
        return fallback
    return "좋음" if value else "확인 필요"


def _format_risk(
    score: float | None, level: str | None, reason: str | None
) -> str:
    if score is None:
        return "리스크 점수 정보 없음"
    level_text = level or "등급 정보 없음"
    reason_text = reason or "리스크 사유 확인 필요"
    return f"리스크 점수 {score}점 ({level_text}) - {reason_text}"


def _format_score(score: float | None) -> str:
    if score is None:
        return "추천 점수 정보 없음"
    return f"기본 추천 점수 {score}점"


def _format_student_note(
    near_univ: bool | None, near_transport: bool | None, near_mart: bool | None
) -> str:
    notes: list[str] = []
    if near_univ is True:
        notes.append("캠퍼스 접근성이 우수합니다.")
    elif near_univ is False:
        notes.append("캠퍼스와의 거리는 추가 확인이 필요합니다.")
    if near_transport is True:
        notes.append("대중교통 이동이 편리합니다.")
    elif near_transport is False:
        notes.append("대중교통 접근성은 확인이 필요합니다.")
    if near_mart is True:
        notes.append("근처 편의시설이 있어 생활비 절감에 도움이 됩니다.")
    elif near_mart is False:
        notes.append("편의시설 정보는 확인이 필요합니다.")
    return " ".join(notes) if notes else "주변 환경 정보는 확인이 필요합니다."
