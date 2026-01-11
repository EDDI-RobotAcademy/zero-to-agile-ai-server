from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Sequence

from pydantic import BaseModel

from modules.house_platform.domain.value_object.house_platform_domain import (
    HousePlatformDomainType,
)

# --- Dataclasses (Internal/Legacy/Crawler usage) ---

@dataclass
class HousePlatformUpsertModel:
    """house_platform 저장에 필요한 필드 묶음."""

    house_platform_id: int | None = None
    title: str | None = None
    address: str | None = None
    deposit: int | None = None
    abang_user_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    registered_at: datetime | None = None
    domain_id: int | HousePlatformDomainType | None = HousePlatformDomainType.ZIGBANG
    rgst_no: str | None = None
    snapshot_id: str | None = None
    pnu_cd: str | None = None
    is_banned: bool | None = None
    sales_type: str | None = None
    monthly_rent: int | None = None
    room_type: str | None = None
    residence_type: str | None = None
    contract_area: float | None = None
    exclusive_area: float | None = None
    floor_no: int | None = None
    all_floors: int | None = None
    lat_lng: Mapping[str, float] | None = None
    manage_cost: int | None = None
    can_park: bool | None = None
    has_elevator: bool | None = None
    image_urls: Sequence[str] | None = None
    gu_nm: str | None = None
    dong_nm: str | None = None


@dataclass
class HousePlatformManagementUpsertModel:
    """관리비 포함/제외 내역 저장 모델."""

    house_platform_management_id: int | None = None
    house_platform_id: int | None = None
    management_included: str | None = None
    management_excluded: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class HousePlatformOptionUpsertModel:
    """옵션/주변 인프라 규칙 기반 저장 모델."""

    house_platform_options_id: int | None = None
    house_platform_id: int | None = None
    built_in: Sequence[str] | None = None
    near_univ: bool | None = None
    near_transport: bool | None = None
    near_mart: bool | None = None
    nearby_pois: Sequence[Mapping[str, Any]] | None = None


# --- Pydantic Models (API usage) ---

class HousePlatformCreateRequest(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    deposit: Optional[int] = None
    domain_id: Optional[int] = 1
    rgst_no: Optional[str] = None
    sales_type: Optional[str] = None
    monthly_rent: Optional[int] = None
    room_type: Optional[str] = None
    contract_area: Optional[float] = None
    exclusive_area: Optional[float] = None
    floor_no: Optional[int] = None
    all_floors: Optional[int] = None
    lat_lng: Optional[Dict[str, Any]] = None
    manage_cost: Optional[int] = None
    can_park: Optional[bool] = None
    has_elevator: Optional[bool] = None
    image_urls: Optional[str] = None
    pnu_cd: Optional[str] = None
    is_banned: Optional[bool] = False
    residence_type: Optional[str] = None
    gu_nm: Optional[str] = None
    dong_nm: Optional[str] = None
    snapshot_id: Optional[str] = None


class HousePlatformUpdateRequest(BaseModel):
    title: Optional[str] = None
    address: Optional[str] = None
    deposit: Optional[int] = None
    rgst_no: Optional[str] = None
    sales_type: Optional[str] = None
    monthly_rent: Optional[int] = None
    room_type: Optional[str] = None
    contract_area: Optional[float] = None
    exclusive_area: Optional[float] = None
    floor_no: Optional[int] = None
    all_floors: Optional[int] = None
    lat_lng: Optional[Dict[str, Any]] = None
    manage_cost: Optional[int] = None
    can_park: Optional[bool] = None
    has_elevator: Optional[bool] = None
    image_urls: Optional[str] = None
    pnu_cd: Optional[str] = None
    is_banned: Optional[bool] = None
    residence_type: Optional[str] = None
    gu_nm: Optional[str] = None
    dong_nm: Optional[str] = None
    snapshot_id: Optional[str] = None


class HousePlatformResponse(BaseModel):
    house_platform_id: int
    title: Optional[str]
    address: Optional[str]
    deposit: Optional[int]
    domain_id: Optional[int]
    rgst_no: Optional[str]
    sales_type: Optional[str]
    monthly_rent: Optional[int]
    room_type: Optional[str]
    contract_area: Optional[float]
    exclusive_area: Optional[float]
    floor_no: Optional[int]
    all_floors: Optional[int]
    lat_lng: Optional[Dict[str, Any]]
    manage_cost: Optional[int]
    can_park: Optional[bool]
    has_elevator: Optional[bool]
    image_urls: Optional[str]
    pnu_cd: Optional[str]
    is_banned: Optional[bool]
    residence_type: Optional[str]
    gu_nm: Optional[str]
    dong_nm: Optional[str]
    registered_at: Optional[datetime]
    crawled_at: Optional[datetime]
    snapshot_id: Optional[str]
    abang_user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    phone_number: Optional[str] = None

    class Config:
        from_attributes = True