from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence


@dataclass
class HousePlatformUpsertModel:
    house_platform_id: int | None = None
    title: str | None = None
    address: str | None = None
    deposit: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    domain_id: int | None = 1
    rgst_no: str | None = None
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
