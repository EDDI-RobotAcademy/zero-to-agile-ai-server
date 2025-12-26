"""house_platform soft delete 수동 실행 러너."""
from __future__ import annotations

import argparse
import logging
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.house_platform.application.dto.delete_house_platform_dto import (
    DeleteHousePlatformCommand,
)
from modules.house_platform.application.usecase.delete_house_platform import (
    DeleteHousePlatformService,
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
        "--house-platform-id",
        type=int,
        required=True,
        help="soft delete 대상 house_platform_id",
    )
    parser.add_argument("--reason", default=None, help="삭제 사유")
    return parser.parse_args()


def build_usecase() -> DeleteHousePlatformService:
    """리포지토리를 연결해 삭제 유스케이스를 만든다."""
    repository = HousePlatformRepository()
    return DeleteHousePlatformService(repository)


def main():
    """입력된 ID로 soft delete를 실행한다."""
    args = parse_args()
    usecase = build_usecase()
    command = DeleteHousePlatformCommand(
        house_platform_id=args.house_platform_id, reason=args.reason
    )
    result = usecase.execute(command)
    logger.info(
        "soft delete 결과 id=%s deleted=%s already_deleted=%s message=%s",
        result.house_platform_id,
        result.deleted,
        result.already_deleted,
        result.message,
    )


if __name__ == "__main__":
    main()
