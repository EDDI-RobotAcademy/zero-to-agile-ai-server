from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FinderRequest:
    """
    임차인(tenant)의 매물 요구 조건을 나타내는 도메인 모델
    """
    abang_user_id: int
    status: str  # Y: 활성, N: 비활성
    finder_request_id: Optional[int] = None
    preferred_region: Optional[str] = None
    price_type: Optional[str] = None  # JEONSE, MONTHLY, MIXED
    max_deposit: Optional[int] = None
    max_rent: Optional[int] = None
    house_type: Optional[str] = None
    additional_condition: Optional[str] = None
    university_name: Optional[str] = None
    roomcount: Optional[str] = None
    bathroomcount: Optional[str] = None
    is_near: bool = False
    aircon_yn: str = "N"
    washer_yn: str = "N"
    fridge_yn: str = "N"
    max_building_age: int = 5
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """요구서가 활성 상태인지 확인"""
        return self.status == "Y"

    def deactivate(self):
        """요구서를 비활성화"""
        self.status = "N"
