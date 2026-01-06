from infrastructure.db.postgres import SessionLocal
from modules.university.adapter.output.university_repository import UniversityRepository
from modules.university.application.usecase.get_universities_usecase import GetUniversitiesUseCase

_university_repo = None

def get_university_repository():
    global _university_repo
    if _university_repo is None:
        _university_repo = UniversityRepository(SessionLocal)
    return _university_repo

def get_get_universities_usecase():
    return GetUniversitiesUseCase(get_university_repository())
