from typing import Optional, Protocol
from modules.abang_user.domain.app_user import AppUser

class AbangUserRepositoryPort(Protocol):
    def find_by_id(self, user_id: int) -> Optional[AppUser]:
        """ID로 사용자 조회"""
        ...
        
    def update(self, user: AppUser) -> Optional[AppUser]:
        """사용자 정보 수정"""
        ...
