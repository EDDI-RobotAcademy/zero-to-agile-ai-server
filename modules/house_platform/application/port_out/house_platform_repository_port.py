from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence, Set

from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)


class HousePlatformRepositoryPort(ABC):
    """house_platform 저장소 추상화."""

    @abstractmethod
    def exists_rgst_nos(self, rgst_nos: Iterable[str]) -> Set[str]:
        """이미 저장된 rgst_no 목록을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def upsert_batch(self, bundles: Sequence[HousePlatformUpsertBundle]) -> int:
        """배치 업서트 후 저장 건수를 반환한다."""
        raise NotImplementedError
