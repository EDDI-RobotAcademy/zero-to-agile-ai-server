from __future__ import annotations

from typing import Sequence

from sqlalchemy import or_

from infrastructure.db.postgres import SessionLocal
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidate,
    FilterCandidateCriteria,
)
from modules.student_house_decision_policy.application.port_out.house_platform_candidate_port import (
    HousePlatformCandidateReadPort,
)


class HousePlatformCandidateRepository(HousePlatformCandidateReadPort):
    """house_platform 후보 조회 저장소."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or SessionLocal

    def fetch_candidates(
        self, criteria: FilterCandidateCriteria, limit: int | None = None
    ) -> Sequence[FilterCandidate]:
        """조건을 만족하는 house_platform 후보를 조회한다."""
        session = self._session_factory()
        try:
            query = (
                session.query(
                    HousePlatformORM.house_platform_id,
                    HousePlatformORM.deposit,
                    HousePlatformORM.monthly_rent,
                    HousePlatformORM.manage_cost,
                )
                .filter(
                    or_(
                        HousePlatformORM.is_banned.is_(False),
                        HousePlatformORM.is_banned.is_(None),
                    )
                )
                # 보증금 누락 매물은 제외한다.
                .filter(HousePlatformORM.deposit.isnot(None))
            )

            query = self._apply_budget_filters(query, criteria)
            query = self._apply_request_filters(query, criteria)

            if limit is not None:
                query = query.limit(limit)
            rows = query.all()
            return [
                FilterCandidate(
                    house_platform_id=row[0],
                    deposit=int(row[1]),
                    monthly_rent=int(row[2]) if row[2] is not None else None,
                    manage_cost=int(row[3]) if row[3] is not None else None,
                )
                for row in rows
            ]
        finally:
            session.close()

    @staticmethod
    def _apply_budget_filters(query, criteria: FilterCandidateCriteria):
        """예산 관련 필터를 적용한다."""
        if criteria.max_deposit_limit is not None:
            query = query.filter(
                HousePlatformORM.deposit <= criteria.max_deposit_limit
            )

        if criteria.price_type:
            # 전세는 월세가 없을 수 있어 monthly_rent 필터를 완화한다.
            price_key = criteria.price_type.upper()
            if price_key == "JEONSE":
                query = query.filter(
                    HousePlatformORM.sales_type.ilike("%전세%")
                )
            elif price_key == "MONTHLY":
                query = query.filter(
                    HousePlatformORM.sales_type.ilike("%월세%")
                )
                query = query.filter(HousePlatformORM.monthly_rent.isnot(None))
            elif price_key == "MIXED":
                query = query.filter(
                    or_(
                        HousePlatformORM.sales_type.ilike("%전세%"),
                        HousePlatformORM.sales_type.ilike("%월세%"),
                    )
                )
                query = query.filter(
                    or_(
                        HousePlatformORM.sales_type.ilike("%전세%"),
                        HousePlatformORM.monthly_rent.isnot(None),
                    )
                )
        else:
            query = query.filter(
                or_(
                    HousePlatformORM.sales_type.ilike("%전세%"),
                    HousePlatformORM.monthly_rent.isnot(None),
                )
            )

        if criteria.max_rent_limit is not None:
            price_key = criteria.price_type.upper() if criteria.price_type else ""
            if price_key != "JEONSE":
                if price_key == "MONTHLY":
                    query = query.filter(
                        HousePlatformORM.monthly_rent
                        <= criteria.max_rent_limit
                    )
                else:
                    query = query.filter(
                        or_(
                            HousePlatformORM.sales_type.ilike("%전세%"),
                            HousePlatformORM.monthly_rent
                            <= criteria.max_rent_limit,
                        )
                    )
        return query

    @staticmethod
    def _apply_request_filters(query, criteria: FilterCandidateCriteria):
        """예산 외 입력 조건을 적용한다."""
        if criteria.preferred_region:
            region_token = _extract_region_token(criteria.preferred_region)
            if region_token:
                query = query.filter(
                    HousePlatformORM.address.ilike(f"%{region_token}%")
                )
        # TODO: house_type 매핑 규칙 확정 전까지 필터를 비활성화한다.
        # TODO: house_type 매핑 규칙을 정교화한다.
        # TODO: additional_condition 해석 규칙이 확정되면 필터를 추가한다.
        return query


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
