from __future__ import annotations

from abc import ABC, abstractmethod

from modules.house_platform.application.dto.fetch_and_store_dto import (
    FetchAndStoreCommand,
    FetchAndStoreResult,
)


class FetchAndStoreHousePlatformPort(ABC):
    """house_platform 크롤링/저장 유스케이스 인터페이스."""

    @abstractmethod
    def execute(self, command: FetchAndStoreCommand) -> FetchAndStoreResult:
        """크롤링 조건을 받아 저장 결과를 반환한다."""
        raise NotImplementedError
