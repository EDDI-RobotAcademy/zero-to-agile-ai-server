from __future__ import annotations

from abc import ABC, abstractmethod

from modules.house_platform.application.dto.monitor_house_platform_dto import (
    MonitorHousePlatformCommand,
    MonitorHousePlatformResult,
)


class MonitorHousePlatformPort(ABC):
    """house_platform 모니터링 유스케이스 포트."""

    @abstractmethod
    def execute(
        self, command: MonitorHousePlatformCommand
    ) -> MonitorHousePlatformResult:
        """모니터링을 수행한다."""
        raise NotImplementedError
