from typing import Optional
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort

class GetUserPhoneUseCase:
    """
    사용자 전화번호 조회 유스케이스
    """
    def __init__(self, repository: AbangUserRepositoryPort):
        self.repository = repository
        
    def execute(self, user_id: int) -> Optional[str]:
        """
        사용자 ID로 전화번호를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            전화번호 (없으면 None)
        """
        user = self.repository.find_by_id(user_id)
        if not user:
            return None
            
        return user.phone_number
