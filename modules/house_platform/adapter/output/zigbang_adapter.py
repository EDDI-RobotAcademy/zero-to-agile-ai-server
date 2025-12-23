"""직방 응답을 house_platform 업서트 모델로 변환."""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping, Sequence, Tuple

from modules.house_platform.application.dto.fetch_and_store_dto import (
    HousePlatformUpsertBundle,
)
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformManagementUpsertModel,
    HousePlatformOptionUpsertModel,
    HousePlatformUpsertModel,
)
from modules.house_platform.application.port_out.zigbang_fetch_port import (
    ZigbangFetchPort,
)
from modules.house_platform.domain.value_object.house_platform_domain import (
    HousePlatformDomainType,
)


class ZigbangAdapter:
    """직방 API 결과를 저장 모델로 정규화한다."""

    def __init__(self, fetch_port: ZigbangFetchPort):
        self.fetch_port = fetch_port

    def fetch_and_convert_by_item_ids(
        self,
        item_ids: Iterable[int],
        region_filters: Sequence[str] | None = None,
    ) -> Tuple[list[HousePlatformUpsertBundle], list[str]]:
        """item_id 목록을 상세 조회하여 업서트 번들로 변환한다."""
        region_filters = list(region_filters or [])
        errors: list[str] = []
        normalized_ids = self._normalize_item_ids(item_ids)
        if not normalized_ids:
            return [], ["유효한 item_id가 없습니다."]

        try:
            summary_items = self.fetch_port.fetch_by_item_ids(normalized_ids)
        except Exception as exc:  # noqa: BLE001
            return [], [f"배치 조회 실패: {exc}"]

        filtered = self._filter_by_region(summary_items, region_filters)
        return self._convert_details(filtered, errors)

    def _convert_details(
        self,
        items: Sequence[Mapping[str, Any]],
        errors: list[str],
    ) -> Tuple[list[HousePlatformUpsertBundle], list[str]]:
        """상세 조회 후 매핑 결과와 에러를 모아 반환한다."""
        converted: list[HousePlatformUpsertBundle] = []
        for item in items:
            item_id = item.get("item_id") or item.get("itemId")
            if not item_id:
                errors.append("item_id 없음")
                continue
            try:
                detail = self.fetch_port.fetch_detail(int(item_id))
                converted.append(self._map_raw_item_to_bundle(detail))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"상세 조회/매핑 실패 {item_id}: {exc}")
        return converted, errors

    def _normalize_item_ids(self, item_ids: Iterable[Any]) -> list[int]:
        normalized: list[int] = []
        for raw in item_ids:
            if isinstance(raw, Mapping):
                val = raw.get("item_id") or raw.get("itemId")
            else:
                val = raw
            try:
                if val is not None:
                    normalized.append(int(val))
            except (TypeError, ValueError):
                continue
        return normalized

    def _filter_by_region(
        self, raw_items: Sequence[Mapping], region_filters: Sequence[str]
    ) -> list[Mapping]:
        if not region_filters:
            return list(raw_items)
        filtered = []
        for item in raw_items:
            full_text = (
                item.get("addressOrigin", {}).get("fullText")
                or item.get("address")
                or ""
            )
            if any(region in full_text for region in region_filters):
                filtered.append(item)
        return filtered

    def _map_raw_item_to_bundle(
        self, raw_item: Mapping[str, Any]
    ) -> HousePlatformUpsertBundle:
        """직방 상세 응답을 house_platform/관리비/옵션으로 매핑한다."""
        item = dict(raw_item)
        price = item.get("price", {}) or {}
        area = item.get("area", {}) or {}
        floor_info = item.get("floor", {}) or {}
        manage_cost = item.get("manageCost", {}) or {}
        manage_cost_detail = item.get("manageCostDetail", {}) or {}
        address_origin = item.get("addressOrigin", {}) or {}

        rgst_no = item.get("itemId")
        if not rgst_no:
            raise ValueError("rgst_no(itemId)가 없습니다.")

        house_platform = HousePlatformUpsertModel(
            title=item.get("title"),
            address=self._merge_address(
                address_origin.get("fullText"), item.get("jibunAddress")
            ),
            deposit=self._to_int(price.get("deposit")),
            domain_id=HousePlatformDomainType.ZIGBANG,
            rgst_no=str(rgst_no),
            pnu_cd=self._parse_pnu_cd(item.get("pnu")),
            sales_type=item.get("salesType"),
            monthly_rent=self._to_int(price.get("rent")),
            room_type=item.get("roomType"),
            contract_area=self._to_float(area.get("계약면적M2")),
            exclusive_area=self._to_float(area.get("전용면적M2")),
            floor_no=self._to_int(floor_info.get("floor")),
            all_floors=self._to_int(floor_info.get("allFloors")),
            lat_lng=self._extract_lat_lng(item),
            manage_cost=self._extract_manage_cost_amount(
                manage_cost, manage_cost_detail
            ),
            can_park=self._parse_parking(item),
            has_elevator=item.get("elevator"),
            image_urls=self._normalize_images(item.get("images")),
        )

        included = self._extract_manage_list(manage_cost, "includes", "include")
        excluded = self._extract_manage_list(manage_cost, "notIncludes", "exclude")
        management = None
        if included or excluded:
            management = HousePlatformManagementUpsertModel(
                management_included=self._serialize_list(included),
                management_excluded=self._serialize_list(excluded),
            )

        options_raw = item.get("options")
        options = None
        if isinstance(options_raw, list):
            options = [
                HousePlatformOptionUpsertModel(option=str(opt))
                for opt in options_raw
                if opt
            ]

        return HousePlatformUpsertBundle(
            house_platform=house_platform,
            management=management,
            options=options,
        )

    @staticmethod
    def _to_int(value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_images(value: Any) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return [str(v) for v in value if v]
        return None

    @staticmethod
    def _extract_lat_lng(item: Mapping[str, Any]) -> Mapping[str, float] | None:
        raw = item.get("location") or item.get("randomLocation") or {}
        lat = raw.get("lat")
        lng = raw.get("lng")
        try:
            if lat is None or lng is None:
                return None
            return {"lat": float(lat), "lng": float(lng)}
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _extract_manage_cost_amount(
        manage_cost: Mapping[str, Any],
        manage_cost_detail: Mapping[str, Any],
    ) -> int | None:
        detail_amount = manage_cost_detail.get("avgManageCost")
        if detail_amount is not None:
            return ZigbangAdapter._normalize_amount(detail_amount)
        return ZigbangAdapter._normalize_amount(manage_cost.get("amount"))

    @staticmethod
    def _normalize_amount(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if not match:
                return None
            value = match.group()
        try:
            num = int(value)
        except (TypeError, ValueError):
            return None
        if num == 0:
            return 0
        return num * 10000 if num < 1000 else num

    @staticmethod
    def _parse_parking(item: Mapping[str, Any]) -> bool | None:
        text = item.get("parkingAvailableText")
        if text:
            if any(word in str(text) for word in ["불가", "없음", "불가능"]):
                return False
            return True
        count_text = item.get("parkingCountText")
        if count_text:
            if any(word in str(count_text) for word in ["없음", "불가", "불가능"]):
                return False
            return True
        return None

    @staticmethod
    def _extract_manage_list(
        manage_cost: Mapping[str, Any], list_key: str, alt_key: str
    ) -> list[str]:
        values = manage_cost.get(list_key)
        if isinstance(values, list) and values:
            return [str(v).strip() for v in values if v]
        alt = manage_cost.get(alt_key)
        if isinstance(alt, list) and alt:
            output = []
            for item in alt:
                if isinstance(item, Mapping):
                    output.append(
                        str(item.get("name") or item.get("code") or "").strip()
                    )
                else:
                    output.append(str(item).strip())
            return [v for v in output if v]
        return []

    @staticmethod
    def _serialize_list(values: list[str]) -> str | None:
        if not values:
            return None
        return json.dumps(values, ensure_ascii=False)

    @staticmethod
    def _parse_pnu_cd(value: Any) -> int | None:
        """PNU 문자열을 int8 범위의 정수로 변환한다."""
        if value is None:
            return None
        if isinstance(value, int):
            return value
        digits = re.sub(r"\D", "", str(value))
        if not digits:
            return None
        try:
            return int(digits)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _merge_address(full_text: str | None, jibun: str | None) -> str:
        if full_text and jibun:
            if jibun.startswith(full_text):
                return jibun.strip()
            if full_text.startswith(jibun):
                return full_text.strip()
            tokens = full_text.split()
            if len(tokens) > 1:
                tail = " ".join(tokens[1:])
                if jibun.startswith(tail):
                    return f"{tokens[0]} {jibun}".strip()
            return f"{full_text} {jibun}".strip()
        return (full_text or jibun or "").strip()
