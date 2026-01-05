from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class StudentHouseScoreResult:
    """학생 추천 점수 계산 결과."""

    house_platform_id: int
    price_score: float
    option_score: float
    risk_score: float
    base_total_score: float
    is_student_recommended: bool


@dataclass
class StudentHouseScoreSource:
    """스코어 계산용 원본 데이터."""

    house_platform_id: int
    address: str | None
    pnu_cd: str | None
    monthly_rent: int | None
    manage_cost: int | None
    built_in: Sequence[str] | None


@dataclass
class StudentHouseCandidateQuery:
    """후보군 조회 입력."""

    university_name: str
    campus: str | None = None
    limit: int = 20


@dataclass
class StudentHouseCandidateRaw:
    """후보군 조회를 위한 원본 데이터."""

    house_platform_id: int
    base_total_score: float
    lat: float | None
    lng: float | None


@dataclass
class StudentHouseCandidatePool:
    """추천 후보군 풀 정보."""

    student_house_id: int
    house_platform_id: int
    base_total_score: float


@dataclass
class StudentHouseDetail:
    """추천 결과 조립용 상세 정보."""

    student_house_id: int
    house_platform_id: int
    base_total_score: float
    risk_score: float | None
    address: str | None
    title: str | None
    domain_id: int | None
    rgst_no: str | None
    sales_type: str | None
    deposit: int | None
    monthly_rent: int | None
    manage_cost: int | None
    room_type: str | None
    residence_type: str | None
    contract_area: float | None
    exclusive_area: float | None
    floor_no: int | None
    all_floors: int | None
    lat_lng: dict | None
    can_park: bool | None
    has_elevator: bool | None
    image_urls: Sequence[str] | None
    created_at: str | None
    updated_at: str | None
    built_in: Sequence[str] | None
    near_univ: bool | None
    near_transport: bool | None
    near_mart: bool | None
    management_included: Sequence[str] | None
    management_excluded: Sequence[str] | None


@dataclass
class StudentHouseCandidate:
    """후보군 조회 결과."""

    house_platform_id: int
    distance_km: float
    distance_score: float
    base_total_score: float
    total_score: float


@dataclass
class StudentHouseSemanticSource:
    """임베딩 문장 생성용 입력."""

    student_house_id: int
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
    risk_score: float | None
    risk_level: str | None
    risk_reason: str | None
    base_total_score: float | None
    semantic_description: str | None


@dataclass
class StudentHouseEmbeddingUpsert:
    """임베딩 업서트 입력."""

    student_house_id: int
    embedding: list[float]
    semantic_description: str | None = None


@dataclass
class StudentHouseEmbeddingResult:
    total: int
    embedded: int
    saved: int
    skipped: int
    errors: list[str] = field(default_factory=list)
