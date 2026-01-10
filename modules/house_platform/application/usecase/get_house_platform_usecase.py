from typing import List, Optional
from modules.house_platform.application.port_out.house_platform_repository_port import HousePlatformRepositoryPort
from modules.house_platform.domain.house_platform import HousePlatform

class GetHousePlatformUseCase:
    def __init__(self, repository: HousePlatformRepositoryPort):
        self.repository = repository

    def execute_get_by_id(self, house_platform_id: int) -> Optional[HousePlatform]:
        return self.repository.find_by_id(house_platform_id)

    def execute_get_all_by_user(self, user_id: int) -> List[HousePlatform]:
        return self.repository.find_all_by_user_id(user_id)
