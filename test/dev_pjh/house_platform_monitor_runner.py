"""house_platform 최신 상태 모니터 수동 실행 러너."""
from __future__ import annotations

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.house_platform.application.dto.monitor_house_platform_dto import (
    MonitorHousePlatformCommand,
)
from modules.house_platform.application.usecase.monitor_house_platform import (
    MonitorHousePlatformService,
)
from modules.house_platform.infrastructure.client.zigbang_api_client import (
    ZigbangApiClient,
)
from modules.house_platform.infrastructure.repository.house_platform_repository import (
    HousePlatformRepository,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """러너 실행 옵션을 파싱한다."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--since-minutes",
        type=int,
        default=15,
        help="updated_at 기준 경과 시간(분)",
    )
    parser.add_argument("--limit", type=int, default=50, help="최대 처리 건수")
    return parser.parse_args()


def build_usecase() -> MonitorHousePlatformService:
    """클라이언트/리포지토리를 엮어 유스케이스를 구성한다."""
    client = ZigbangApiClient()
    repository = HousePlatformRepository()
    return MonitorHousePlatformService(client, repository)


def main() -> None:
    """모니터링을 실행한다."""
    load_dotenv()
    args = parse_args()
    usecase = build_usecase()
    cmd = MonitorHousePlatformCommand(
        since_minutes=args.since_minutes, limit=args.limit
    )
    result = usecase.execute(cmd)
    logger.info(
        "[모니터링] checked=%s updated=%s skipped=%s banned=%s errors=%s",
        result.checked,
        result.updated,
        result.skipped,
        result.banned,
        len(result.errors),
    )
    for err in result.errors:
        logger.warning("에러: %s", err)


if __name__ == "__main__":
    main()
