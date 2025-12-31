from __future__ import annotations

from abc import ABC, abstractmethod

from modules.house_platform.application.dto.delete_house_platform_dto import (
    DeleteHousePlatformCommand,
    DeleteHousePlatformResult,
)


class DeleteHousePlatformPort(ABC):
    """house_platform soft delete 유스케이스 인터페이스."""

    @abstractmethod
    def execute(self, command: DeleteHousePlatformCommand) -> DeleteHousePlatformResult:
        """삭제 요청을 처리하고 결과를 반환한다."""
        raise NotImplementedError
