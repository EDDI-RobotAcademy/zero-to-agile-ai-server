from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeleteHousePlatformCommand:
    """house_platform soft delete 입력."""

    house_platform_id: int
    reason: str | None = None


@dataclass
class DeleteHousePlatformResult:
    """soft delete 결과 정보."""

    house_platform_id: int
    deleted: bool
    already_deleted: bool = False
    message: str | None = None
