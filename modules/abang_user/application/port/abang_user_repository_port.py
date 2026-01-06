from typing import Optional, Protocol
from modules.abang_user.domain.app_user import AppUser

class AbangUserRepositoryPort(Protocol):
    def find_by_id(self, user_id: int) -> Optional[AppUser]:
        """ID로 사용자 조회"""
        ...
