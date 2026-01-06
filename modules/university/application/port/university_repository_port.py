from typing import List, Protocol

class UniversityRepositoryPort(Protocol):
    def get_all_university_names(self) -> List[str]:
        """모든 대학교 이름을 중복 없이 조회하여 가나다순으로 반환"""
        ...
