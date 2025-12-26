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

        summary_items, errors = self.adapter.fetch_summary_items(command.item_ids or [])
        fetched = len(summary_items)
        if not summary_items:
            return FetchAndStoreResult(fetched=0, stored=0, skipped=0, errors=errors)

        filtered = self.adapter.filter_by_region(summary_items, self.region_filters)
        if not filtered:
            return FetchAndStoreResult(
                fetched=fetched, stored=0, skipped=fetched, errors=errors
            )

        summary_ids = self.adapter.collect_item_ids(filtered)
        existing = (
            self.repository_port.exists_rgst_nos(summary_ids)
            if summary_ids
            else set()
        )
        filtered = [
            item
            for item in filtered
            if str(item.get("item_id") or item.get("itemId")) not in existing
        ]

        bundles, errors = self.adapter.convert_details(
            filtered, errors, skip_ids=existing
        )
        stored = self.repository_port.upsert_batch(bundles) if bundles else 0
        skipped = fetched - len(bundles)

        return FetchAndStoreResult(
            fetched=fetched, stored=stored, skipped=skipped, errors=errors
        )
