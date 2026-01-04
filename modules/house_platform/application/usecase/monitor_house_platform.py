from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Mapping

from modules.house_platform.adapter.output.zigbang_adapter import ZigbangAdapter
from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformOptionUpsertModel,
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
    return _normalize_bundle(existing) == _normalize_bundle(incoming)


def _normalize_bundle(bundle: HousePlatformUpsertBundle) -> dict[str, Any]:
    return {
        "house_platform": _normalize_house_platform(bundle.house_platform),
        "management": _normalize_management(bundle.management),
        "options": _normalize_options(bundle.options),
    }


def _normalize_house_platform(model) -> dict[str, Any]:
    data = asdict(model) if model else {}
    data.pop("house_platform_id", None)
    data.pop("updated_at", None)
    data["is_banned"] = bool(data.get("is_banned", False))
    data["created_at"] = _to_iso(data.get("created_at"))
    data["registered_at"] = _to_iso(data.get("registered_at"))
    data["image_urls"] = _normalize_list(data.get("image_urls"))
    data["lat_lng"] = _normalize_lat_lng(data.get("lat_lng"))
    return data


def _normalize_management(model) -> dict[str, Any] | None:
    if not model:
        return None
    data = asdict(model)
    data.pop("house_platform_management_id", None)
    data.pop("created_at", None)
    data.pop("updated_at", None)
    included = _normalize_list_value(data.get("management_included"))
    excluded = _normalize_list_value(data.get("management_excluded"))
    if not included and not excluded:
        return None
    return {
        "management_included": included,
        "management_excluded": excluded,
    }


def _normalize_options(model: HousePlatformOptionUpsertModel | None) -> dict | None:
    if not model:
        return None
    data = asdict(model)
    data.pop("house_platform_options_id", None)
    data.pop("house_platform_id", None)
    built_in = _normalize_list_value(data.get("built_in"))
    nearby_pois = _normalize_nearby_pois(data.get("nearby_pois"))
    if not built_in and not any(
        [
            data.get("near_univ"),
            data.get("near_transport"),
            data.get("near_mart"),
            nearby_pois,
        ]
    ):
        return None
    return {
        "built_in": built_in,
        "near_univ": data.get("near_univ"),
        "near_transport": data.get("near_transport"),
        "near_mart": data.get("near_mart"),
        "nearby_pois": nearby_pois,
    }


def _normalize_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]
    return None


def _normalize_list_value(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return sorted([str(item) for item in value if item])
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return sorted([value]) if value else None
        if isinstance(parsed, list):
            return sorted([str(item) for item in parsed if item])
    return None


def _normalize_lat_lng(value: Any) -> dict[str, float] | None:
    if not value or not isinstance(value, Mapping):
        return None
    lat = value.get("lat")
    lng = value.get("lng")
    try:
        if lat is None or lng is None:
            return None
        return {"lat": float(lat), "lng": float(lng)}
    except (TypeError, ValueError):
        return None


def _normalize_nearby_pois(value: Any) -> list[dict[str, Any]] | None:
    if not value:
        return None
    if not isinstance(value, list):
        return None
    normalized: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        poi_type = item.get("poiType")
        distance = item.get("distance")
        payload: dict[str, Any] = {}
        if poi_type:
            payload["poiType"] = poi_type
        if distance is not None:
            try:
                payload["distance"] = int(float(distance))
            except (TypeError, ValueError):
                pass
        if payload:
            normalized.append(payload)
    normalized.sort(key=lambda row: (row.get("poiType", ""), row.get("distance", 0)))
    return normalized or None


def _to_iso(value: Any) -> str | None:
    if not value:
        return None
    try:
        return value.isoformat()
    except AttributeError:
        return None
