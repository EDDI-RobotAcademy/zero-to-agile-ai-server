from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformManagementUpsertModel,
    HousePlatformOptionUpsertModel,
    HousePlatformUpsertModel,
)


@dataclass
class FetchAndStoreCommand:
    """크롤링 입력 조건."""

    item_ids: Sequence[int] | None = None

    def has_no_filter(self) -> bool:
        """필터 미설정 여부를 판단한다."""
        return not self.item_ids


@dataclass
class FetchAndStoreResult:
    """크롤링 + 저장 결과."""

    fetched: int
    stored: int
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class HousePlatformUpsertBundle:
    """매물/관리비/옵션을 묶어 저장하기 위한 단위."""

    house_platform: HousePlatformUpsertModel
    management: HousePlatformManagementUpsertModel | None = None
    options: HousePlatformOptionUpsertModel | None = None
