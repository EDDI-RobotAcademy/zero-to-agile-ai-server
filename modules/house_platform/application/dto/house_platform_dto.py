from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from modules.house_platform.domain.value_object.house_platform_domain import (
    HousePlatformDomainType,
)

@dataclass
class HousePlatformUpsertModel:
    """house_platform 저장에 필요한 필드 묶음."""

    house_platform_id: int | None = None
    title: str | None = None
    address: str | None = None
    deposit: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    domain_id: int | HousePlatformDomainType | None = HousePlatformDomainType.ZIGBANG
    rgst_no: str | None = None
    pnu_cd: int | None = None
    sales_type: str | None = None
    monthly_rent: int | None = None
    room_type: str | None = None
    contract_area: float | None = None
    exclusive_area: float | None = None
    floor_no: int | None = None
    all_floors: int | None = None
    lat_lng: Mapping[str, float] | None = None
    manage_cost: int | None = None
    can_park: bool | None = None
    has_elevator: bool | None = None
    image_urls: Sequence[str] | None = None


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
    """옵션 정규화 저장 모델."""

    house_platform_options_id: int | None = None
    house_platform_id: int | None = None
    option: str | None = None
