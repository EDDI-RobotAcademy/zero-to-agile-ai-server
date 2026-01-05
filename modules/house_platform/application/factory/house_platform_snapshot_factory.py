from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformOptionUpsertModel,
)


def build_house_platform_snapshot_id(bundle: HousePlatformUpsertBundle) -> str:
    """house_platform 스냅샷 ID를 생성한다."""
    payload = normalize_house_platform_bundle(bundle, include_snapshot_id=False)
    serialized = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def normalize_house_platform_bundle(
    bundle: HousePlatformUpsertBundle, include_snapshot_id: bool = True
) -> dict[str, Any]:
    """스냅샷/비교용으로 번들을 정규화한다."""
    return {
        "house_platform": _normalize_house_platform(
            bundle.house_platform, include_snapshot_id=include_snapshot_id
        ),
        "management": _normalize_management(bundle.management),
        "options": _normalize_options(bundle.options),
    }


def _normalize_house_platform(model, include_snapshot_id: bool) -> dict[str, Any]:
    data = asdict(model) if model else {}
    data.pop("house_platform_id", None)
    data.pop("updated_at", None)
    if not include_snapshot_id:
        data.pop("snapshot_id", None)
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
