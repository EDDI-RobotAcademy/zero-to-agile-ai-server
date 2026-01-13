from typing import List, Protocol

from modules.university.application.dto.university_location_dto import (
    UniversityLocationDTO,
)

class UniversityRepositoryPort(Protocol):
    def get_all_university_names(self) -> List[str]:
        """모든 대학교 이름을 중복 없이 조회하여 가나다순으로 반환"""
        ...

    def get_university_locations(self) -> List[UniversityLocationDTO]:
        """대학 위치 목록을 조회하여 반환"""
        ...

    def get_unique_university_locations(self) -> List[int]:
        """주소가 중복되지 않는 대학 위치 ID 목록을 반환"""
        ...
