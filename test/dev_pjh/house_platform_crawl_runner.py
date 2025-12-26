"""house_platform 직방 크롤링 수동 실행 러너."""
from __future__ import annotations

import argparse
import logging
import os
import random
import sys
import time

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.house_platform.infrastructure.repository.house_platform_repository import (
    HousePlatformRepository,
)
from modules.house_platform.application.dto.fetch_and_store_dto import (
    FetchAndStoreCommand,
)
from modules.house_platform.application.usecase.fetch_and_store_house_platform import (
    FetchAndStoreHousePlatformService,
)
from modules.house_platform.infrastructure.client.zigbang_api_client import (
    ZigbangApiClient,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """러너 실행 옵션을 파싱한다."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--item-ids", default="", help="수동 실행용 item_id 목록")
    parser.add_argument("--start-id", type=int, default=None, help="범위 시작 id")
    parser.add_argument("--end-id", type=int, default=None, help="범위 종료 id")
    parser.add_argument(
        "--region-filters",
        default="",
        help="지역 필터(콤마 구분, 예: 마포구,서대문구)",
    )
    parser.add_argument("--interval-items", type=int, default=None)
    parser.add_argument("--interval-minutes", type=int, default=None)
    parser.add_argument("--chunk-size", type=int, default=15)
    parser.add_argument("--sleep-min", type=float, default=3)
    parser.add_argument("--sleep-max", type=float, default=7)
    return parser.parse_args()


def build_usecase(region_filters: list[str]) -> FetchAndStoreHousePlatformService:
    """클라이언트/리포지토리를 엮어 유스케이스를 구성한다."""
    client = ZigbangApiClient()
    repository = HousePlatformRepository()
    return FetchAndStoreHousePlatformService(
        client, repository, region_filters=region_filters
    )


def parse_item_ids(raw: str) -> list[int]:
    """쉼표로 구분된 item_id를 정수 리스트로 변환한다."""
    if not raw:
        return []
    result = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            result.append(int(token))
        except ValueError:
            continue
    return result


def chunked(iterable, size: int):
    """반복자를 지정 크기 청크로 분리한다."""
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def run_once(usecase: FetchAndStoreHousePlatformService, args: argparse.Namespace):
    """입력된 item_id로 단발성 크롤링을 수행한다."""
    item_ids = parse_item_ids(args.item_ids)
    cmd = FetchAndStoreCommand(item_ids=item_ids or None)
    result = usecase.execute(cmd)
    logger.info(
        "[크롤링] fetched=%s stored=%s skipped=%s errors=%s",
        result.fetched,
        result.stored,
        result.skipped,
        len(result.errors),
    )
    for err in result.errors:
        logger.warning("에러: %s", err)


def run_range_crawl(
    usecase: FetchAndStoreHousePlatformService, args: argparse.Namespace
):
    """범위 item_id를 청크로 나누어 연속 크롤링한다."""
    if args.start_id is None or args.end_id is None:
        raise ValueError("start-id/end-id가 필요합니다.")
    fetched = 0
    stored = 0
    skipped = 0
    errors: list[str] = []
    for chunk in chunked(range(args.start_id, args.end_id + 1), args.chunk_size):
        cmd = FetchAndStoreCommand(item_ids=chunk)
        result = usecase.execute(cmd)
        fetched += result.fetched
        stored += result.stored
        skipped += result.skipped
        errors.extend(result.errors)
        time.sleep(random.uniform(args.sleep_min, args.sleep_max))
        logger.info(
            "[청크] ids=%s..%s fetched=%s stored=%s skipped=%s errors=%s",
            chunk[0],
            chunk[-1],
            result.fetched,
            result.stored,
            result.skipped,
            len(result.errors),
        )
    logger.info(
        "[범위크롤 종료] fetched=%s stored=%s skipped=%s errors=%s",
        fetched,
        stored,
        skipped,
        len(errors),
    )
    for err in errors:
        logger.warning("에러: %s", err)

def parse_region_filters(args: argparse.Namespace) -> list[str]:
    """환경변수/인자를 결합해 지역 필터를 만든다."""
    raw = args.region_filters
    if not raw:
        raw = os.getenv("ZIGBANG_CRAWL_SEOUL_REGIONS", "")
    return [token.strip() for token in raw.split(",") if token.strip()]


def resolve_interval_minutes(args: argparse.Namespace) -> int:
    """스케줄러 간격을 결정한다."""
    if args.interval_minutes:
        return args.interval_minutes
    env_value = os.getenv("ZIGBANG_CRAWL_INTERVAL_MINUTES")
    try:
        return int(env_value) if env_value else 60
    except ValueError:
        return 60


def resolve_interval_items(args: argparse.Namespace) -> int:
    """한 사이클에 처리할 item_id 개수를 결정한다."""
    if args.interval_items:
        return args.interval_items
    env_value = os.getenv("ZIGBANG_CRAWL_INTERVAL_ITEMS")
    try:
        return int(env_value) if env_value else 10000
    except ValueError:
        return 10000


def resolve_range(args: argparse.Namespace) -> tuple[int | None, int | None]:
    """크롤링 범위를 인자/환경변수에서 결정한다."""
    start_id = args.start_id
    end_id = args.end_id
    if start_id is None:
        start_env = os.getenv("ZIGBANG_CRAWL_START_ID")
        start_id = int(start_env) if start_env and start_env.isdigit() else None
    if end_id is None:
        end_env = os.getenv("ZIGBANG_CRAWL_END_ID")
        end_id = int(end_env) if end_env and end_env.isdigit() else None
    return start_id, end_id


def _state_path() -> str:
    return os.path.join(CURRENT_DIR, ".crawl_state_house_platform")


def _load_state() -> dict[str, int]:
    path = _state_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            return {"next_start": int(content)} if content else {}
    except Exception:
        return {}


def _save_state(next_start: int) -> None:
    try:
        with open(_state_path(), "w", encoding="utf-8") as file:
            file.write(str(next_start))
    except Exception:
        logger.warning("상태 저장 실패 next_start=%s", next_start)


def run_stateful_crawl(
    usecase: FetchAndStoreHousePlatformService,
    args: argparse.Namespace,
    start_id: int,
    end_id: int,
):
    """crawl_state 기반으로 일정 단위씩 순차 크롤링한다."""
    interval_items = resolve_interval_items(args)
    interval_minutes = resolve_interval_minutes(args)
    state = _load_state()
    next_start = state.get("next_start", start_id)
    if next_start < start_id or next_start > end_id:
        next_start = start_id

    while True:
        if next_start > end_id:
            logger.info("크롤링 종료: end_id 도달 next_start=%s", next_start)
            return

        cycle_end = min(next_start + interval_items - 1, end_id)
        logger.info(
            "[사이클] start=%s end=%s interval_items=%s",
            next_start,
            cycle_end,
            interval_items,
        )

        fetched = 0
        stored = 0
        skipped = 0
        errors: list[str] = []

        for chunk in chunked(range(next_start, cycle_end + 1), args.chunk_size):
            cmd = FetchAndStoreCommand(item_ids=chunk)
            result = usecase.execute(cmd)
            fetched += result.fetched
            stored += result.stored
            skipped += result.skipped
            errors.extend(result.errors)
            _save_state(chunk[-1] + 1)
            time.sleep(random.uniform(args.sleep_min, args.sleep_max))
            logger.info(
                "[청크] ids=%s..%s fetched=%s stored=%s skipped=%s errors=%s",
                chunk[0],
                chunk[-1],
                result.fetched,
                result.stored,
                result.skipped,
                len(result.errors),
            )

        next_start = cycle_end + 1
        _save_state(next_start)
        logger.info(
            "[사이클 종료] fetched=%s stored=%s skipped=%s errors=%s",
            fetched,
            stored,
            skipped,
            len(errors),
        )
        if errors:
            for err in errors:
                logger.warning("에러: %s", err)

        if next_start > end_id:
            logger.info("크롤링 종료: end_id 도달 next_start=%s", next_start)
            return
        logger.info("다음 사이클까지 %s분 대기", interval_minutes)
        time.sleep(interval_minutes * 60)


def main():
    """실행 인자에 따라 단발/범위 크롤링을 선택한다."""
    load_dotenv()
    args = parse_args()
    region_filters = parse_region_filters(args)
    usecase = build_usecase(region_filters)
    item_ids = parse_item_ids(args.item_ids)
    if item_ids:
        run_once(usecase, args)
        return

    start_id, end_id = resolve_range(args)
    if start_id is None or end_id is None:
        raise ValueError("범위 시작/종료 ID가 설정되지 않았습니다.")
    run_stateful_crawl(usecase, args, start_id, end_id)


if __name__ == "__main__":
    main()
