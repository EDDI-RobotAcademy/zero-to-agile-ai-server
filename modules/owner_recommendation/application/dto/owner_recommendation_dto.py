from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel


@dataclass
class OwnerRecommendationRow:
    """추천 후보 조회 결과 단건."""

    house_platform_id: int
    house_title: Optional[str]
    house_address: Optional[str]
    house_sales_type: Optional[str]
    house_residence_type: Optional[str]
    house_monthly_rent: Optional[int]
    house_deposit: Optional[int]
    house_room_type: Optional[str]
    house_gu_nm: Optional[str]
    house_dong_nm: Optional[str]

    finder_request_id: int
    finder_abang_user_id: int
    finder_price_type: Optional[str]
    finder_house_type: Optional[str]
    finder_max_rent: Optional[int]
    finder_preferred_region: Optional[str]


class MatchedFinderRequestResponse(BaseModel):
    finder_request_id: int
    abang_user_id: int
    price_type: Optional[str] = None
    house_type: Optional[str] = None
    max_rent: Optional[int] = None
    preferred_region: Optional[str] = None


class HousePlatformSummaryResponse(BaseModel):
    house_platform_id: int
    title: Optional[str] = None
    address: Optional[str] = None
    sales_type: Optional[str] = None
    residence_type: Optional[str] = None
    monthly_rent: Optional[int] = None
    deposit: Optional[int] = None
    room_type: Optional[str] = None
    gu_nm: Optional[str] = None
    dong_nm: Optional[str] = None


class OwnerRecommendationItemResponse(BaseModel):
    house_platform: HousePlatformSummaryResponse
    matched_finder_requests: List[MatchedFinderRequestResponse]


class OwnerRecommendationResponse(BaseModel):
    abang_user_id: int
    rent_margin: int
    total_recommended_houses: int
    total_matched_requests: int
    results: List[OwnerRecommendationItemResponse]
