from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MonitorHousePlatformCommand:
    """모니터링 대상 조건."""

    since_minutes: int = 15
    limit: int | None = None


@dataclass
class MonitorHousePlatformResult:
    """모니터링 결과."""

    checked: int
    updated: int
    skipped: int
    banned: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class HousePlatformMonitorTarget:
    """모니터링 대상 요약 정보."""

    house_platform_id: int
    domain_id: int | None
    rgst_no: str | None
    updated_at: datetime | None = None
    is_banned: bool | None = None
