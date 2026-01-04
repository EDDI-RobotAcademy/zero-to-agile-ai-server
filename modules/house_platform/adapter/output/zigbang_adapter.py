"""직방 응답을 house_platform 업서트 모델로 변환."""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
        summary_items, errors = self.fetch_summary_items(item_ids)
        if not summary_items:
            return [], errors
        filtered = self.filter_by_region(summary_items, region_filters or [])
        return self.convert_details(filtered, errors)

    def fetch_summary_items(
        self, item_ids: Iterable[int]
    ) -> Tuple[list[Mapping[str, Any]], list[str]]:
        """item_id 목록을 요약 API로 조회한다."""
        normalized_ids = self._normalize_item_ids(item_ids)
        if not normalized_ids:
            return [], ["유효한 item_id가 없습니다."]
        try:
            summary_items = self.fetch_port.fetch_by_item_ids(normalized_ids)
        except Exception as exc:  # noqa: BLE001
            return [], [f"배치 조회 실패: {exc}"]
        return list(summary_items), []

    def convert_details(
        self,
        items: Sequence[Mapping[str, Any]],
        errors: list[str] | None = None,
        skip_ids: set[str] | None = None,
    ) -> Tuple[list[HousePlatformUpsertBundle], list[str]]:
        """상세 조회 후 매핑 결과와 에러를 모아 반환한다."""
        errors = list(errors or [])
        skip_ids = skip_ids or set()
        converted: list[HousePlatformUpsertBundle] = []
        for item in items:
            item_id = item.get("item_id") or item.get("itemId")
            if not item_id:
                errors.append("item_id 없음")
                continue
            if str(item_id) in skip_ids:
                continue
            try:
                detail = self.fetch_port.fetch_detail(int(item_id))
                converted.append(self._map_raw_item_to_bundle(detail))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"상세 조회/매핑 실패 {item_id}: {exc}")
        return converted, errors

    def convert_detail_item(
        self, raw_item: Mapping[str, Any]
    ) -> HousePlatformUpsertBundle:
        """직방 상세 응답을 업서트 번들로 변환한다."""
        return self._map_raw_item_to_bundle(raw_item)

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

    def filter_by_region(
        self, raw_items: Sequence[Mapping], region_filters: Sequence[str]
    ) -> list[Mapping]:
        """요약 응답의 local1/local2 기준으로 지역 필터링한다."""
        if not region_filters:
            return list(raw_items)
        filtered = []
        for item in raw_items:
            address_origin = item.get("addressOrigin", {}) or {}
            local1 = address_origin.get("local1") or ""
            full_text = address_origin.get("fullText") or item.get("address") or ""
            if local1:
                if local1 not in {"서울시", "서울특별시"}:
                    continue
            else:
                if "서울" not in full_text:
                    continue
            local2 = address_origin.get("local2") or ""
            if local2 and any(region in local2 for region in region_filters):
                filtered.append(item)
                continue
            if any(region in full_text for region in region_filters):
                filtered.append(item)
        return filtered

    def collect_item_ids(self, items: Sequence[Mapping[str, Any]]) -> list[str]:
        """요약 응답에서 item_id 목록을 추출한다."""
        collected: list[str] = []
        for item in items:
            item_id = item.get("item_id") or item.get("itemId")
            if item_id is None:
                continue
            collected.append(str(item_id))
        return collected

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
            room_type=item.get("roomType") or item.get("serviceType"),
            residence_type=item.get("residenceType"),
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
            created_at=self._parse_datetime(item.get("approveDate")),
            updated_at=self._parse_datetime(item.get("updatedAt")),
            registered_at=self._parse_datetime(item.get("approveDate")),
            gu_nm=address_origin.get("local2"),
            dong_nm=address_origin.get("local3"),
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
        nearby_pois = self._extract_nearby_pois(item)
        options = None
        if isinstance(options_raw, list):
            built_in = self._extract_built_in(options_raw)
            near_flags = self._extract_near_flags(item)
            if built_in or any(near_flags.values()) or nearby_pois:
                options = HousePlatformOptionUpsertModel(
                    built_in=built_in or None,
                    near_univ=near_flags.get("near_univ"),
                    near_transport=near_flags.get("near_transport"),
                    near_mart=near_flags.get("near_mart"),
                    nearby_pois=nearby_pois,
                )
        else:
            near_flags = self._extract_near_flags(item)
            if any(near_flags.values()) or nearby_pois:
                options = HousePlatformOptionUpsertModel(
                    built_in=None,
                    near_univ=near_flags.get("near_univ"),
                    near_transport=near_flags.get("near_transport"),
                    near_mart=near_flags.get("near_mart"),
                    nearby_pois=nearby_pois,
                )

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
            return [ZigbangAdapter._apply_image_params(str(v)) for v in value if v]
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
        return num // 10000 if num >= 1000 else num

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
    def _normalize_options(values: list[Any]) -> list[str]:
        """옵션 목록을 정제하고 중복을 제거한다."""
        seen = set()
        result: list[str] = []
        for raw in values:
            if raw is None:
                continue
            text = str(raw).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(text)
        return result

    @staticmethod
    def _extract_built_in(values: list[Any]) -> list[str]:
        """옵션에서 빌트인 항목만 추출한다."""
        normalized = ZigbangAdapter._normalize_options(values)
        targets = ["에어컨", "냉장고", "세탁기"]
        built_in: list[str] = []
        for item in normalized:
            for target in targets:
                if target in item and target not in built_in:
                    built_in.append(target)
        return built_in

    @staticmethod
    def _extract_near_flags(item: Mapping[str, Any]) -> dict[str, bool]:
        """주변 인프라 정보를 rule base로 판별한다."""
        neighborhoods = item.get("neighborhoods", {}) or {}
        amenities = [
            amenity.get("title")
            for amenity in neighborhoods.get("amenities", [])
            if isinstance(amenity, Mapping)
        ]
        nearby_pois = neighborhoods.get("nearbyPois", []) or []

        def has_amenity(keyword: str) -> bool:
            for title in amenities:
                if not title:
                    continue
                if keyword in str(title):
                    return True
            return False

        def within_10min(poi: Mapping[str, Any]) -> bool:
            distance = poi.get("distance")
            time_taken = poi.get("timeTaken")
            if distance is not None:
                try:
                    if float(distance) <= 660:
                        return True
                except (TypeError, ValueError):
                    pass
            if time_taken is not None:
                try:
                    if float(time_taken) <= 600:
                        return True
                except (TypeError, ValueError):
                    pass
            return False

        def near_poi(poi_types: set[str]) -> bool:
            for poi in nearby_pois:
                if not isinstance(poi, Mapping):
                    continue
                if not poi.get("exists"):
                    continue
                if poi.get("poiType") not in poi_types:
                    continue
                if within_10min(poi):
                    return True
            return False

        near_univ = near_poi({"대학교", "대학"}) or has_amenity("대학")
        near_transport = near_poi({"지하철역", "버스정류장"}) or has_amenity("역세권")
        near_mart = near_poi({"편의점", "대형마트"})

        return {
            "near_univ": near_univ,
            "near_transport": near_transport,
            "near_mart": near_mart,
        }

    @staticmethod
    def _extract_nearby_pois(
        item: Mapping[str, Any],
    ) -> list[dict[str, Any]] | None:
        """exists=true POI만 추출하여 저장용 JSON으로 만든다."""
        neighborhoods = item.get("neighborhoods", {}) or {}
        nearby_pois = neighborhoods.get("nearbyPois", []) or []
        results: list[dict[str, Any]] = []
        for poi in nearby_pois:
            if not isinstance(poi, Mapping):
                continue
            if not poi.get("exists"):
                continue
            poi_type = poi.get("poiType")
            distance = poi.get("distance")
            payload: dict[str, Any] = {}
            if poi_type:
                payload["poiType"] = poi_type
            if distance is not None:
                try:
                    payload["distance"] = int(float(distance))
                except (TypeError, ValueError):
                    pass
            if payload:
                results.append(payload)
        return results or None

    @staticmethod
    def _apply_image_params(url: str) -> str:
        """이미지 URL에 접근 가능한 파라미터를 부여한다."""
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.update({"w": "0", "h": "640", "a": "1"})
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        """도메인 날짜 문자열을 datetime으로 변환한다."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        raw = str(value)
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%Y.%m.%d",
            "%Y-%m-%d",
            "%Y%m%d",
            "%Y년 %m월 %d일",
            "%Y년%m월%d일",
            "%Y년 %m월 %d일 %H:%M",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _parse_pnu_cd(value: Any) -> str | None:
        """PNU 값을 숫자 문자열로 정규화한다."""
        if value is None:
            return None
        if isinstance(value, int):
            return str(value)
        digits = re.sub(r"\D", "", str(value))
        if not digits:
            return None
        return digits

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
