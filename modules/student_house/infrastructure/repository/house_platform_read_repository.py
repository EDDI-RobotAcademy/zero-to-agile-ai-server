from __future__ import annotations

import json

from sqlalchemy import or_
from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.house_platform.infrastructure.orm.house_platform_options_orm import (
    HousePlatformOptionORM,
)
from modules.student_house.application.dto.student_house_dto import (
    StudentHouseScoreSource,
)
from modules.student_house.application.port_out.house_platform_read_port import (
    HousePlatformReadPort,
)
from infrastructure.db.session_helper import open_session


class HousePlatformReadRepository(HousePlatformReadPort):
    """student_house용 house_platform 조회 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def get_house_detail(
        self, house_platform_id: int
    ) -> StudentHouseScoreSource | None:
        """house_platform과 옵션을 조인해 반환한다."""
        session, generator = open_session(self._session_factory)
        try:
            row = (
                session.query(HousePlatformORM, HousePlatformOptionORM)
                .outerjoin(
                    HousePlatformOptionORM,
                    HousePlatformOptionORM.house_platform_id
                    == HousePlatformORM.house_platform_id,
                )
                .filter(HousePlatformORM.house_platform_id == house_platform_id)
                .filter(
                    or_(
                        HousePlatformORM.is_banned.is_(False),
                        HousePlatformORM.is_banned.is_(None),
                    )
                )
                .one_or_none()
            )
            if not row:
                return None
            house, options = row
            return StudentHouseScoreSource(
                house_platform_id=house.house_platform_id,
                address=house.address,
                pnu_cd=house.pnu_cd,
                monthly_rent=house.monthly_rent,
                manage_cost=house.manage_cost,
                built_in=_parse_json_list(options.built_in) if options else None,
            )
        finally:
            if generator:
                generator.close()
            else:
                session.close()


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
