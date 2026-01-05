"""finder_request 임베딩 일괄 생성 러너."""
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
from infrastructure.db.session_helper import open_session
from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.finder_request.adapter.output.finder_request_model import (
    FinderRequestModel,
)
from modules.finder_request.application.factory.finder_request_embedding_factory import (
    build_finder_request_embedding_text,
)
from modules.finder_request.domain.finder_request import FinderRequest
from modules.finder_request.infrastructure.repository.finder_request_embedding_repository import (
    FinderRequestEmbeddingRepository,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_batch_size() -> int:
    raw = os.getenv("FINDER_REQUEST_EMBED_BATCH_SIZE", "200")
    try:
        return int(raw)
    except ValueError:
        return 200


def _get_concurrency() -> int:
    raw = os.getenv("FINDER_REQUEST_EMBED_CONCURRENCY", "5")
    try:
        return int(raw)
    except ValueError:
        return 5


def _fetch_all_requests() -> list[FinderRequest]:
    session, generator = open_session(get_db_session)
    try:
        rows = session.query(FinderRequestModel).all()
        return [_to_domain(row) for row in rows]
    finally:
        if generator:
            generator.close()
        else:
            session.close()


def _to_domain(model: FinderRequestModel) -> FinderRequest:
    return FinderRequest(
        abang_user_id=model.abang_user_id,
        status=model.status,
        finder_request_id=model.finder_request_id,
        preferred_region=model.preferred_region,
        price_type=model.price_type,
        max_deposit=model.max_deposit,
        max_rent=model.max_rent,
        house_type=model.house_type,
        additional_condition=model.additional_condition,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


async def main() -> None:
    load_dotenv()
    batch_size = _get_batch_size()
    concurrency = _get_concurrency()

    requests = _fetch_all_requests()
    if not requests:
        logger.info("처리할 finder_request 데이터가 없습니다.")
        return

    embedder = OpenAIEmbeddingAgent()
    repository = FinderRequestEmbeddingRepository()

    logger.info(
        "임베딩 시작 (batch_size=%s concurrency=%s dummy=%s)",
        batch_size,
        concurrency,
        embedder.is_dummy(),
    )

    batches = _chunked(requests, batch_size)
    errors: list[str] = []
    embedded = 0
    saved = 0

    for i in range(0, len(batches), max(concurrency, 1)):
        chunk = batches[i : i + max(concurrency, 1)]
        results = await asyncio.gather(
            *(_process_batch(batch, embedder, repository) for batch in chunk),
            return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue
            batch_embedded, batch_saved = result
            embedded += batch_embedded
            saved += batch_saved

    logger.info(
        "임베딩 완료 total=%s embedded=%s saved=%s skipped=%s errors=%s",
        len(requests),
        embedded,
        saved,
        len(requests) - embedded,
        len(errors),
    )
    for err in errors:
        logger.warning("에러: %s", err)


async def _process_batch(
    batch: list[FinderRequest],
    embedder: OpenAIEmbeddingAgent,
    repository: FinderRequestEmbeddingRepository,
) -> tuple[int, int]:
    texts = [build_finder_request_embedding_text(req) for req in batch]
    vectors = await embedder.embed_texts(texts)
    saved = 0
    for req, vector in zip(batch, vectors):
        repository.upsert_embedding(req.finder_request_id, vector)
        saved += 1
    return len(vectors), saved


def _chunked(items: list[FinderRequest], size: int) -> list[list[FinderRequest]]:
    if size <= 0:
        return [list(items)]
    chunks: list[list[FinderRequest]] = []
    buf: list[FinderRequest] = []
    for item in items:
        buf.append(item)
        if len(buf) >= size:
            chunks.append(buf)
            buf = []
    if buf:
        chunks.append(buf)
    return chunks


if __name__ == "__main__":
    asyncio.run(main())
