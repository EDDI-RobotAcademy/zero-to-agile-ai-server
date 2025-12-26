from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class HousePlatformSemanticSource:
    """임베딩 대상이 되는 매물 요약 정보."""

    house_platform_id: int
    address: str | None
    room_type: str | None
    residence_type: str | None
    deposit: int | None
    monthly_rent: int | None
    manage_cost: int | None
    contract_area: float | None
    exclusive_area: float | None
    floor_no: int | None
    all_floors: int | None
    can_park: bool | None
    has_elevator: bool | None
    built_in: Sequence[str] | None
    near_univ: bool | None
    near_transport: bool | None
    near_mart: bool | None
    management_included: Sequence[str] | None
    management_excluded: Sequence[str] | None
    semantic_description: str | None


@dataclass
class EmbedRequest:
    record_id: int
    text: str


@dataclass
class EmbedResult:
    record_id: int
    vector: list[float]


@dataclass
class HousePlatformEmbeddingUpsert:
    house_platform_id: int
    embedding: list[float]
    semantic_description: str | None = None


@dataclass
class HousePlatformEmbeddingResult:
    total: int
    embedded: int
    saved: int
    skipped: int
    errors: list[str] = field(default_factory=list)
