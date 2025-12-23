"""직방 API 호출 클라이언트."""
from __future__ import annotations

import logging
import random
import time
from typing import Iterable, Mapping, Sequence

import requests

from modules.house_platform.application.port_out.zigbang_fetch_port import (
    ZigbangFetchPort,
)

logger = logging.getLogger(__name__)


class ZigbangApiClient(ZigbangFetchPort):
    """직방 API 호출 및 재시도/지연 정책을 캡슐화한다."""

    def __init__(
        self,
        base_url: str = "https://apis.zigbang.com/v3",
        min_delay_sec: float = 0.5,
        max_delay_sec: float = 1.5,
        session: requests.Session | None = None,
        max_retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.min_delay_sec = min_delay_sec
        self.max_delay_sec = max_delay_sec
        self.session = session or requests.Session()
        self.max_retries = max_retries

    def fetch_by_item_ids(self, item_ids: Iterable[int]) -> Sequence[Mapping]:
        """item_id를 15개씩 묶어 배치 조회한다."""
        item_ids_list = list(item_ids)
        if not item_ids_list:
            return []

        results: list[Mapping] = []
        url = "https://apis.zigbang.com/house/property/v1/items/list"
        chunk_size = 15
        headers = self._headers(with_extra=True)

        for i in range(0, len(item_ids_list), chunk_size):
            chunk = item_ids_list[i : i + chunk_size]
            success = False
            for attempt in range(1, self.max_retries + 2):
                try:
                    resp = self.session.post(
                        url,
                        headers=headers,
                        json={"itemIds": chunk},
                        timeout=10,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("items", [])
                    results.extend(items)
                    success = True
                    break
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "직방 배치 요청 실패 items=%s attempt=%s/%s err=%s",
                        chunk,
                        attempt,
                        self.max_retries + 1,
                        exc,
                    )
                    self._sleep_with_jitter()
            if not success:
                logger.error("직방 배치 요청 연속 실패, chunk=%s", chunk)

        return results

    def fetch_detail(self, item_id: int) -> Mapping:
        """단건 상세를 조회하고 지터 딜레이를 적용한다."""
        url = f"{self.base_url}/items/{item_id}"
        try:
            return self._retry_detail(url, item_id)
        finally:
            self._sleep_with_jitter()

    def _retry_detail(self, url: str, item_id: int) -> Mapping:
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                resp = self.session.get(
                    url,
                    headers=self._headers(),
                    params={"version": "", "domain": "zigbang"},
                    timeout=10,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("item") or data
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning(
                    "상세 요청 실패 item_id=%s attempt=%s/%s err=%s",
                    item_id,
                    attempt,
                    self.max_retries + 1,
                    exc,
                )
                self._sleep_with_jitter()
        raise last_exc or RuntimeError("상세 요청 실패")

    def _sleep_with_jitter(self):
        time.sleep(random.uniform(self.min_delay_sec, self.max_delay_sec))

    def _headers(self, with_extra: bool = False) -> dict[str, str]:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/16.4 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/119.0 Safari/537.36",
        ]
        base = {
            "User-Agent": random.choice(user_agents),
            "Accept": "application/json",
        }
        if with_extra:
            base.update(
                {
                    "content-type": "application/json",
                    "origin": "https://www.zigbang.com",
                    "referer": "https://www.zigbang.com/",
                    "x-zigbang-platform": "www",
                }
            )
        return base
