from typing import List
from sqlalchemy.orm import Session
from modules.university.application.port.university_repository_port import UniversityRepositoryPort
from modules.university.adapter.output.university_model import UniversityLocation

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
