from typing import List
from modules.university.application.port.university_repository_port import UniversityRepositoryPort

class GetUniversitiesUseCase:
    def __init__(self, repository: UniversityRepositoryPort):
        self.repository = repository

    def execute(self) -> List[str]:
        return self.repository.get_all_university_names()
