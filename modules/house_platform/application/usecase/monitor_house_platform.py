from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Mapping

from modules.house_platform.adapter.output.zigbang_adapter import ZigbangAdapter
from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.factory.house_platform_snapshot_factory import (
    build_house_platform_snapshot_id,
    normalize_house_platform_bundle,
)
from modules.house_platform.application.dto.monitor_house_platform_dto import (
    MonitorHousePlatformCommand,
    MonitorHousePlatformResult,
)
from modules.house_platform.application.port_in.monitor_house_platform_port import (
    MonitorHousePlatformPort,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)
from modules.house_platform.application.port_out.zigbang_fetch_port import (
    ZigbangFetchPort,
)
from modules.house_platform.domain.value_object.house_platform_domain import (
    HousePlatformDomainType,
)


class MonitorHousePlatformService(MonitorHousePlatformPort):
    """house_platform 최신 상태 모니터링 유스케이스."""

    def __init__(
        self,
        fetch_port: ZigbangFetchPort,
        repository_port: HousePlatformRepositoryPort,
    ):
        self.fetch_port = fetch_port
        self.repository_port = repository_port
        self.adapter = ZigbangAdapter(fetch_port)

    def execute(
        self, command: MonitorHousePlatformCommand
    ) -> MonitorHousePlatformResult:
        """updated_at 기준으로 대상 매물의 변경 여부를 확인한다."""
        cutoff = datetime.now() - timedelta(minutes=command.since_minutes)
        targets = self.repository_port.fetch_monitor_targets(
            cutoff, limit=command.limit
        )

        checked = 0
        updated = 0
        skipped = 0
        banned = 0
        errors: list[str] = []

        for target in targets:
            checked += 1
            if target.domain_id != HousePlatformDomainType.ZIGBANG:
                skipped += 1
                continue
            if not target.rgst_no:
                skipped += 1
                continue
            try:
                detail = self.fetch_port.fetch_detail(int(target.rgst_no))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"상세 조회 실패 {target.rgst_no}: {exc}")
                continue

            bundle = self.adapter.convert_detail_item(detail)
            if _is_closed(detail):
                bundle.house_platform.is_banned = True
                banned += 1

            # 업데이트 시각은 시스템 onupdate에 맡긴다.
            bundle.house_platform.updated_at = None
            # 스냅샷 ID를 생성해 저장에 반영한다.
            bundle.house_platform.snapshot_id = build_house_platform_snapshot_id(
                bundle
            )

            existing = self.repository_port.fetch_bundle_by_id(
                target.house_platform_id
            )
            if existing and _is_same_bundle(existing, bundle):
                skipped += 1
                continue

            try:
                self.repository_port.upsert_batch([bundle])
                updated += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"업데이트 실패 {target.rgst_no}: {exc}")

        return MonitorHousePlatformResult(
            checked=checked,
            updated=updated,
            skipped=skipped,
            banned=banned,
            errors=errors,
        )


def _is_closed(detail: Mapping[str, Any]) -> bool:
    status = detail.get("status")
    if isinstance(status, bool):
        return not status
    if status is None:
        return False
    value = str(status).strip().lower()
    return value in {"close", "closed", "false", "0", "n"}


def _is_same_bundle(
    existing: HousePlatformUpsertBundle,
    incoming: HousePlatformUpsertBundle,
) -> bool:
    return normalize_house_platform_bundle(
        existing, include_snapshot_id=True
    ) == normalize_house_platform_bundle(incoming, include_snapshot_id=True)
