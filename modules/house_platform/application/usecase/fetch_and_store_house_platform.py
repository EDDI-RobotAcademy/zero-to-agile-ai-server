from __future__ import annotations

from modules.house_platform.adapter.output.zigbang_adapter import ZigbangAdapter
from modules.house_platform.application.dto.fetch_and_store_dto import (
    FetchAndStoreCommand,
    FetchAndStoreResult,
)
from modules.house_platform.application.port_in.fetch_and_store_house_platform_port import (
    FetchAndStoreHousePlatformPort,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)
from modules.house_platform.application.port_out.zigbang_fetch_port import (
    ZigbangFetchPort,
)


class FetchAndStoreHousePlatformService(FetchAndStoreHousePlatformPort):
    """직방 크롤링 → 정제 → 저장 유스케이스."""

    def __init__(
        self,
        fetch_port: ZigbangFetchPort,
        repository_port: HousePlatformRepositoryPort,
        region_filters: list[str] | None = None,
    ):
        self.fetch_port = fetch_port
        self.repository_port = repository_port
        self.region_filters = region_filters or []
        self.adapter = ZigbangAdapter(fetch_port)

    def execute(self, command: FetchAndStoreCommand) -> FetchAndStoreResult:
        """입력 조건을 받아 크롤링/저장을 수행한다."""
        if command.has_no_filter():
            return FetchAndStoreResult(
                fetched=0, stored=0, skipped=0, errors=["크롤링 조건이 없습니다."]
            )

        bundles, errors = self._fetch_and_convert(command)
        if not bundles:
            return FetchAndStoreResult(fetched=0, stored=0, skipped=0, errors=errors)

        rgst_nos = [
            b.house_platform.rgst_no for b in bundles if b.house_platform.rgst_no
        ]
        existing = (
            self.repository_port.exists_rgst_nos(rgst_nos) if rgst_nos else set()
        )
        to_store = [
            b for b in bundles if b.house_platform.rgst_no not in existing
        ]
        skipped = len(bundles) - len(to_store)
        stored = self.repository_port.upsert_batch(to_store) if to_store else 0

        return FetchAndStoreResult(
            fetched=len(bundles), stored=stored, skipped=skipped, errors=errors
        )

    def _fetch_and_convert(self, command: FetchAndStoreCommand):
        if not command.item_ids:
            return [], ["크롤링 조건이 없습니다."]
        return self.adapter.fetch_and_convert_by_item_ids(
            command.item_ids, self.region_filters
        )
