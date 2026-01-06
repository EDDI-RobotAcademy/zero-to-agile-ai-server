from typing import List

from sqlalchemy.orm import Session

from modules.university.adapter.output.university_model import UniversityLocation
from modules.university.application.dto.university_location_dto import (
    UniversityLocationDTO,
)
from modules.university.application.port.university_repository_port import (
    UniversityRepositoryPort,
)

class UniversityRepository(UniversityRepositoryPort):
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def get_all_university_names(self) -> List[str]:
        db: Session = self.db_session_factory()
        try:
            # DISTINCT university_name ORDER BY university_name ASC
            results = db.query(UniversityLocation.university_name)\
                .distinct()\
                .order_by(UniversityLocation.university_name.asc())\
                .all()
            
            # results is list of (university_name,) tuples
            return [row[0] for row in results if row[0]]
        finally:
            db.close()

    def get_university_locations(self) -> List[UniversityLocationDTO]:
        """대학 위치 목록을 조회한다."""
        db: Session = self.db_session_factory()
        try:
            rows = (
                db.query(UniversityLocation)
                .filter(UniversityLocation.lat.isnot(None))
                .filter(UniversityLocation.lng.isnot(None))
                .all()
            )
            return [
                UniversityLocationDTO(
                    university_name=row.university_name,
                    campus=row.campus,
                    lat=float(row.lat),
                    lng=float(row.lng),
                    region=row.region,
                    road_name_address=row.road_name_address,
                    jibun_address=row.jibun_address,
                )
                for row in rows
            ]
        finally:
            db.close()
