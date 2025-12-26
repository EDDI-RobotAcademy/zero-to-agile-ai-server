from __future__ import annotations

from modules.house_platform.application.dto.embedding_dto import (
    HousePlatformSemanticSource,
)


def build_semantic_house_description(source: HousePlatformSemanticSource) -> str:
    """대학생 선호 포인트를 강조한 매물 설명문을 생성한다."""

    lines: list[str] = []
    room_type = _join_text(source.residence_type, source.room_type)

    lines.append("[매물 개요]")
    if source.address and room_type:
        lines.append(f"이 매물은 {source.address}에 위치한 {room_type}입니다.")
    elif source.address:
        lines.append(f"이 매물은 {source.address}에 위치해 있습니다.")
    elif room_type:
        lines.append(f"이 매물은 {room_type} 유형입니다.")
    else:
        lines.append("이 매물은 기본 정보가 부족합니다.")

    floor_desc = _format_floor(source.floor_no, source.all_floors)
    if floor_desc:
        lines.append(f"위치는 {floor_desc}입니다.")

    lines.append("[비용 정보]")
    lines.append(_format_price(source.deposit, source.monthly_rent, source.manage_cost))
    manage_note = _format_manage_notes(
        source.management_included, source.management_excluded
    )
    if manage_note:
        lines.append(manage_note)

    lines.append("[옵션 및 편의시설]")
    option_text = _format_built_in(source.built_in)
    if option_text:
        lines.append(option_text)
    elevator_text = _format_elevator(source.has_elevator)
    if elevator_text:
        lines.append(elevator_text)
    parking_text = _format_parking(source.can_park)
    if parking_text:
        lines.append(parking_text)

    lines.append("[대학생 추천 포인트]")
    lines.append(_format_commute(source.near_univ))
    lines.append(_format_transport(source.near_transport))
    lines.append(_format_mart(source.near_mart))
    safety_note = _format_safety(source.floor_no)
    if safety_note:
        lines.append(safety_note)

    return "\n".join(line for line in lines if line).strip()


def _join_text(*values: str | None) -> str | None:
    joined = " ".join([val for val in values if val])
    return joined or None


def _format_floor(floor_no: int | None, all_floors: int | None) -> str | None:
    if floor_no is None:
        return None
    floor_text = "반지하/지하" if floor_no <= 0 else f"{floor_no}층"
    if all_floors:
        return f"총 {all_floors}층 중 {floor_text}"
    return floor_text


def _format_price(
    deposit: int | None, monthly_rent: int | None, manage_cost: int | None
) -> str:
    deposit_text = f"{deposit}만원" if deposit is not None else "정보 없음"
    rent_text = f"{monthly_rent}만원" if monthly_rent is not None else "정보 없음"
    manage_text = f"{manage_cost}만원" if manage_cost is not None else "정보 없음"
    return f"보증금 {deposit_text}, 월세 {rent_text}, 관리비 {manage_text}입니다."


def _format_manage_notes(
    included: list[str] | None, excluded: list[str] | None
) -> str | None:
    parts = []
    if included:
        parts.append(f"관리비에 포함: {', '.join(included)}")
    if excluded:
        parts.append(f"관리비 불포함: {', '.join(excluded)}")
    return " / ".join(parts) if parts else None


def _format_built_in(built_in: list[str] | None) -> str | None:
    if not built_in:
        return "기본 옵션 정보가 확인되지 않습니다."
    return f"기본 옵션: {', '.join(built_in)}"


def _format_elevator(has_elevator: bool | None) -> str | None:
    if has_elevator is True:
        return "엘리베이터가 있어 짐 이동이 편리합니다."
    if has_elevator is False:
        return "엘리베이터가 없어 이동 동선을 고려해야 합니다."
    return None


def _format_parking(can_park: bool | None) -> str | None:
    if can_park is True:
        return "주차가 가능해 차량 보유자에게 유리합니다."
    if can_park is False:
        return "주차는 어렵습니다."
    return None


def _format_commute(near_univ: bool | None) -> str:
    if near_univ is True:
        return "학교와 가까워 통학이 편리합니다."
    if near_univ is False:
        return "학교와의 거리는 확인이 필요합니다."
    return "학교와의 거리는 추가 확인이 필요합니다."


def _format_transport(near_transport: bool | None) -> str:
    if near_transport is True:
        return "지하철/버스 접근성이 좋아 이동이 편합니다."
    if near_transport is False:
        return "대중교통 접근성은 확인이 필요합니다."
    return "대중교통 접근성은 추가 확인이 필요합니다."


def _format_mart(near_mart: bool | None) -> str:
    if near_mart is True:
        return "편의점/마트 접근이 좋아 생활비 절감에 유리합니다."
    if near_mart is False:
        return "근처 편의시설은 확인이 필요합니다."
    return "편의시설 위치는 추가 확인이 필요합니다."


def _format_safety(floor_no: int | None) -> str | None:
    if floor_no is None:
        return None
    if floor_no >= 2:
        return "사생활 보호와 치안 측면에서 유리한 층수입니다."
    return "저층 매물이라 보안/사생활에 유의하세요."
