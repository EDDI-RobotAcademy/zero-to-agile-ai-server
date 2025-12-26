"""student_house 점수 일괄 생성 러너."""
from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from infrastructure.db.postgres import get_db_session
from modules.house_platform.infrastructure.orm.house_platform_orm import (
    HousePlatformORM,
)
from modules.risk_analysis_mock.adapter.output.risk_analysis_mock_adapter import (
    RiskAnalysisMockAdapter,
)
from modules.student_house.application.usecase.calculate_student_house import (
    CalculateStudentHouseService,
)
from modules.student_house.infrastructure.repository.house_platform_read_repository import (
    HousePlatformReadRepository,
)
from modules.student_house.infrastructure.repository.student_house_repository import (
    StudentHouseRepository,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_concurrency() -> int:
    raw = os.getenv("STUDENT_HOUSE_SCORE_CONCURRENCY", "5")
    try:
        return max(1, int(raw))
    except ValueError:
        return 5


def _fetch_house_platform_ids() -> list[int]:
    session_generator = get_db_session()
    session = next(session_generator)
    try:
        rows = (
            session.query(HousePlatformORM.house_platform_id)
            .filter(
                (HousePlatformORM.is_banned.is_(False))
                | (HousePlatformORM.is_banned.is_(None))
            )
            .order_by(HousePlatformORM.house_platform_id.asc())
            .all()
        )
        return [int(row[0]) for row in rows]
    finally:
        session_generator.close()


async def main() -> None:
    load_dotenv()
    concurrency = _get_concurrency()
    house_ids = _fetch_house_platform_ids()

    if not house_ids:
        logger.info("처리할 house_platform 데이터가 없습니다.")
        return

    house_reader = HousePlatformReadRepository()
    repository = StudentHouseRepository()
    risk_adapter = RiskAnalysisMockAdapter()
    usecase = CalculateStudentHouseService(
        house_reader, repository, risk_adapter
    )

    semaphore = asyncio.Semaphore(concurrency)
    completed = 0
    failed = 0

    async def _run_one(house_id: int) -> None:
        nonlocal completed, failed
        async with semaphore:
            result = await usecase.calculate_and_upsert_score(house_id)
            if result is None:
                failed += 1
            else:
                completed += 1

    tasks = [_run_one(house_id) for house_id in house_ids]
    for chunk in _chunked(tasks, concurrency * 2):
        await asyncio.gather(*chunk)

    logger.info(
        "점수 생성 완료 total=%s success=%s failed=%s",
        len(house_ids),
        completed,
        failed,
    )


def _chunked(items: list[asyncio.Task], size: int):
    buf: list[asyncio.Task] = []
    for item in items:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


if __name__ == "__main__":
    asyncio.run(main())
