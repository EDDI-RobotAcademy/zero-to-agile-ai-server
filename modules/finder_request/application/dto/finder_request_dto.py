from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateFinderRequestDTO:
    """요구서 생성을 위한 Application DTO"""
    abang_user_id: int
    preferred_region: Optional[str] = None
    price_type: Optional[str] = None
    max_deposit: Optional[int] = None
    max_rent: Optional[int] = None
    house_type: Optional[str] = None
    additional_condition: Optional[str] = None
    status: str = 'Y'


@dataclass
class FinderRequestDTO:
    """요구서 조회 결과 Application DTO"""
    finder_request_id: int
    abang_user_id: int
    status: str
    preferred_region: Optional[str] = None
    price_type: Optional[str] = None
    max_deposit: Optional[int] = None
    max_rent: Optional[int] = None
    house_type: Optional[str] = None
    additional_condition: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
