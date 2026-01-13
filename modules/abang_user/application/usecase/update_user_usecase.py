from typing import Optional
from modules.abang_user.application.port.abang_user_repository_port import AbangUserRepositoryPort
from modules.abang_user.application.dto.update_user_dto import UpdateUserDTO
from modules.abang_user.domain.app_user import AppUser

class UpdateUserUseCase:
    """
    사용자 정보 수정 유스케이스
    """
    def __init__(self, abang_user_repository: AbangUserRepositoryPort):
        self.abang_user_repository = abang_user_repository

    def execute(self, dto: UpdateUserDTO) -> Optional[AppUser]:
        """
        사용자 정보를 수정합니다.
        
        Args:
            dto: 수정할 사용자 정보
            
        Returns:
            수정된 사용자 도메인 모델 또는 None
        """
        # 1. 사용자 조회
        user = self.abang_user_repository.find_by_id(dto.user_id)
        if not user:
            return None

        # 2. 도메인 로직 실행 (정보 업데이트)
        user.update_profile(
            phone_number=dto.phone_number,
            university_name=dto.university_name
        )

        # 3. 저장
        updated_user = self.abang_user_repository.update(user)
        
        return updated_user
