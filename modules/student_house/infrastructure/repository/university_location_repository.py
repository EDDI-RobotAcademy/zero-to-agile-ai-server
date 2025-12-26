from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.db.postgres import get_db_session
from modules.student_house.application.port_out.university_location_port import (
    UniversityLocationReadPort,
)
from modules.student_house.infrastructure.orm.university_location_orm import (
    UniversityLocationORM,
)
from infrastructure.db.session_helper import open_session


class UniversityLocationRepository(UniversityLocationReadPort):
    """대학 위치 조회 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or get_db_session

    def get_location(
        self, university_name: str, campus: str | None = None
    ) -> dict | None:
        """대학 위치 정보를 dict로 반환한다."""
        session, generator = open_session(self._session_factory)
        try:
            query = session.query(UniversityLocationORM).filter(
                UniversityLocationORM.university_name == university_name
            )
            if campus:
                query = query.filter(UniversityLocationORM.campus == campus)
            row = query.first()
            if not row:
                return None
            return {
                "university_name": row.university_name,
                "campus": row.campus,
                "lat": row.lat,
                "lng": row.lng,
                "region": row.region,
                "road_name_address": row.road_name_address,
                "jibun_address": row.jibun_address,
            }
        finally:
            if generator:
                generator.close()
            else:
                session.close()
