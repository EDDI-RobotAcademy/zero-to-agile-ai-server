"""student_house 임베딩 일괄 생성 러너."""
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

from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.student_house.application.usecase.generate_student_house_embeddings import (
    GenerateStudentHouseEmbeddingsService,
)
from modules.student_house.infrastructure.repository.student_house_embedding_repository import (
    StudentHouseEmbeddingRepository,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_batch_size() -> int:
    raw = os.getenv("STUDENT_HOUSE_EMBED_BATCH_SIZE", "200")
    try:
        return int(raw)
    except ValueError:
        return 200


def _get_concurrency() -> int:
    raw = os.getenv("STUDENT_HOUSE_EMBED_CONCURRENCY", "5")
    try:
        return int(raw)
    except ValueError:
        return 5


async def main():
    load_dotenv()
    batch_size = _get_batch_size()
    concurrency = _get_concurrency()

    repository = StudentHouseEmbeddingRepository()
    embedder = OpenAIEmbeddingAgent()
    usecase = GenerateStudentHouseEmbeddingsService(
        repository, repository, embedder
    )

    logger.info(
        "임베딩 시작 (batch_size=%s concurrency=%s dummy=%s)",
        batch_size,
        concurrency,
        embedder.is_dummy(),
    )
    result = await usecase.execute(batch_size=batch_size, concurrency=concurrency)
    logger.info(
        "임베딩 완료 total=%s embedded=%s saved=%s skipped=%s errors=%s",
        result.total,
        result.embedded,
        result.saved,
        result.skipped,
        len(result.errors),
    )
    for err in result.errors:
        logger.warning("에러: %s", err)


if __name__ == "__main__":
    asyncio.run(main())
