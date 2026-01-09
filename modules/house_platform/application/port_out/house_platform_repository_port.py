from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Sequence, Set, Optional, List

from modules.house_platform.domain.house_platform import HousePlatform
from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.delete_house_platform_dto import (
    DeleteHousePlatformResult,
)
from modules.house_platform.application.dto.monitor_house_platform_dto import (
    HousePlatformMonitorTarget,
)
from modules.house_platform.application.dto.house_platform_location_dto import (
    HousePlatformLocation,
)


class HousePlatformRepositoryPort(ABC):
    """house_platform 저장소 추상화."""

    @abstractmethod
    def save(self, house_platform: HousePlatform) -> HousePlatform:
        """도메인 객체를 저장하거나 업데이트한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, house_platform_id: int) -> Optional[HousePlatform]:
        """ID로 도메인 객체를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_all_by_user_id(self, abang_user_id: int) -> List[HousePlatform]:
        """사용자 ID로 모든 매물을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, house_platform_id: int) -> bool:
        """ID로 매물을 영구 삭제한다."""
        raise NotImplementedError

    @abstractmethod
    def exists_rgst_nos(self, rgst_nos: Iterable[str]) -> Set[str]:
        """이미 저장된 rgst_no 목록을 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def upsert_batch(self, bundles: Sequence[HousePlatformUpsertBundle]) -> int:
        """배치 업서트 후 저장 건수를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def soft_delete_by_id(self, house_platform_id: int) -> DeleteHousePlatformResult:
        """is_banned 플래그로 삭제 처리한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_monitor_targets(
        self, updated_before, limit: int | None = None
    ) -> Sequence[HousePlatformMonitorTarget]:
        """updated_at 기준 모니터링 대상 목록을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_bundle_by_id(
        self, house_platform_id: int
    ) -> HousePlatformUpsertBundle | None:
        """기존 저장 데이터를 번들 형태로 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def fetch_location_by_id(
        self, house_platform_id: int
    ) -> HousePlatformLocation | None:
        """매물 경위도 정보를 단건 조회한다."""
        raise NotImplementedError
