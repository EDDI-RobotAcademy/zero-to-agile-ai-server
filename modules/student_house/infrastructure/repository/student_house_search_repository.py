from __future__ import annotations

import json
from decimal import Decimal
from typing import Sequence

from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from infrastructure.db.session_helper import open_session
from modules.house_platform.infrastructure.orm.house_platform_management_orm import (
    HousePlatformManagementORM,
)
from modules.house_platform.infrastructure.orm.house_platform_options_orm import (
    HousePlatformOptionORM,
)
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidatePool,
    StudentHouseDetail,
)
from modules.student_house.application.port_out.student_house_search_port import (
    StudentHouseSearchPort,
)
from modules.student_house.infrastructure.orm.student_house_orm import (
    StudentHouseORM,
)


class StudentHouseSearchRepository(StudentHouseSearchPort):
    """finder_request 기반 추천 검색 저장소."""

    STATUS_COMPLETED = "COMPLETED"

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def fetch_candidate_pool(
        self,
        preferred_region: str | None,
        price_type: str | None,
        max_deposit: int | None,
        max_rent: int | None,
        house_type: str | None,
        limit: int = 100,
    ) -> Sequence[StudentHouseCandidatePool]:
        """student_house 상위 후보군을 조회한다."""
        session, generator = open_session(self._session_factory)
        try:
            subq = (
                session.query(
                    StudentHouseORM.student_house_id,
                    StudentHouseORM.house_platform_id,
                    StudentHouseORM.base_total_score,
                )
                .filter(StudentHouseORM.processing_status == self.STATUS_COMPLETED)
                .filter(StudentHouseORM.is_student_recommended.is_(True))
                .order_by(StudentHouseORM.base_total_score.desc())
                .limit(limit)
                .subquery()
            )

            query = (
                session.query(
                    subq.c.student_house_id,
                    subq.c.house_platform_id,
                    subq.c.base_total_score,
                )
                .join(
                    HousePlatformORM,
                    HousePlatformORM.house_platform_id == subq.c.house_platform_id,
                )
                .filter(
                    or_(
                        HousePlatformORM.is_banned.is_(False),
                        HousePlatformORM.is_banned.is_(None),
                    )
                )
            )

            if preferred_region:
                region_token = _extract_region_token(preferred_region)
                if region_token:
                    query = query.filter(
                        HousePlatformORM.address.ilike(
                            f"%{region_token}%"
                        )
                    )
            if max_deposit is not None:
                query = query.filter(HousePlatformORM.deposit <= max_deposit)
            if max_rent is not None:
                query = query.filter(
                    HousePlatformORM.monthly_rent <= max_rent
                )
            if price_type:
                price_key = price_type.upper()
                if price_key == "JEONSE":
                    query = query.filter(
                        HousePlatformORM.sales_type.ilike("%전세%")
                    )
                elif price_key == "MONTHLY":
                    query = query.filter(
                        HousePlatformORM.sales_type.ilike("%월세%")
                    )

            rows = query.all()
            return [
                StudentHouseCandidatePool(
                    student_house_id=row[0],
                    house_platform_id=row[1],
                    base_total_score=float(row[2]),
                )
                for row in rows
            ]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def fetch_details(
        self, student_house_ids: Sequence[int]
    ) -> Sequence[StudentHouseDetail]:
        """추천 결과 조립용 상세 데이터를 조회한다."""
        if not student_house_ids:
            return []
        session, generator = open_session(self._session_factory)
        try:
            rows = (
                session.query(
                    StudentHouseORM,
                    HousePlatformORM,
                    HousePlatformOptionORM,
                    HousePlatformManagementORM,
                )
                .join(
                    HousePlatformORM,
                    HousePlatformORM.house_platform_id
                    == StudentHouseORM.house_platform_id,
                )
                .outerjoin(
                    HousePlatformOptionORM,
                    HousePlatformOptionORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .outerjoin(
                    HousePlatformManagementORM,
                    HousePlatformManagementORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .filter(StudentHouseORM.student_house_id.in_(student_house_ids))
                .all()
            )
            return [self._to_detail(*row) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    def _to_detail(
        self,
        student_house: StudentHouseORM,
        house: HousePlatformORM,
        options: HousePlatformOptionORM | None,
        management: HousePlatformManagementORM | None,
    ) -> StudentHouseDetail:
        return StudentHouseDetail(
            student_house_id=student_house.student_house_id,
            house_platform_id=student_house.house_platform_id,
            base_total_score=float(student_house.base_total_score),
            risk_score=float(student_house.risk_score)
            if student_house.risk_score is not None
            else None,
            address=house.address,
            title=house.title,
            domain_id=house.domain_id,
            rgst_no=house.rgst_no,
            sales_type=house.sales_type,
            deposit=house.deposit,
            monthly_rent=house.monthly_rent,
            manage_cost=house.manage_cost,
            room_type=house.room_type,
            residence_type=house.residence_type,
            contract_area=_to_float(house.contract_area),
            exclusive_area=_to_float(house.exclusive_area),
            floor_no=house.floor_no,
            all_floors=house.all_floors,
            lat_lng=house.lat_lng if house.lat_lng else None,
            can_park=house.can_park,
            has_elevator=house.has_elevator,
            image_urls=_parse_json_list(house.image_urls),
            created_at=_format_dt(house.created_at),
            updated_at=_format_dt(house.updated_at),
            built_in=_parse_json_list(options.built_in) if options else None,
            near_univ=options.near_univ if options else None,
            near_transport=options.near_transport if options else None,
            near_mart=options.near_mart if options else None,
            management_included=_parse_json_list(
                management.management_included
            )
            if management
            else None,
            management_excluded=_parse_json_list(
                management.management_excluded
            )
            if management
            else None,
        )


def _parse_json_list(value: str | None) -> list[str] | None:
    if not value:
        return None
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed if item]
    except Exception:
        return None
    return None


def _to_float(value: Decimal | float | int | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_dt(value) -> str | None:
    if not value:
        return None
    try:
        return value.isoformat()
    except AttributeError:
        return None


def _extract_region_token(preferred_region: str) -> str | None:
    """선호 지역 문자열에서 첫 번째 구 정보를 추출한다."""
    if not preferred_region:
        return None
    tokens = [
        token.strip()
        for token in preferred_region.replace(",", " ").split()
        if token.strip()
    ]
    if not tokens:
        return None
    for token in tokens:
        if token.endswith("구"):
            return token
    return tokens[0]
