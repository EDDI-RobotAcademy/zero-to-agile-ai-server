from __future__ import annotations

from modules.house_platform.application.dto.delete_house_platform_dto import (
    DeleteHousePlatformCommand,
    DeleteHousePlatformResult,
)
from modules.house_platform.application.port_in.delete_house_platform_port import (
    DeleteHousePlatformPort,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)


class DeleteHousePlatformService(DeleteHousePlatformPort):
    """house_platform soft delete 유스케이스."""

    def __init__(self, repository: HousePlatformRepositoryPort):
        self.repository = repository

    def execute(self, command: DeleteHousePlatformCommand) -> DeleteHousePlatformResult:
        """입력 검증 후 저장소에 soft delete를 위임한다."""
        if command.house_platform_id <= 0:
            return DeleteHousePlatformResult(
                house_platform_id=command.house_platform_id,
                deleted=False,
                message="유효하지 않은 house_platform_id 입니다.",
            )
        return self.repository.soft_delete_by_id(command.house_platform_id)
