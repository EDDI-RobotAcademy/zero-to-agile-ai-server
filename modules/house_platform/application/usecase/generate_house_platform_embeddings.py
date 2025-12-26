from __future__ import annotations

import asyncio
from typing import Iterable, Sequence

from modules.house_platform.application.dto.embedding_dto import (
    EmbedRequest,
    HousePlatformEmbeddingResult,
    HousePlatformEmbeddingUpsert,
    HousePlatformSemanticSource,
)
from modules.house_platform.application.factory.house_platform_semantic_factory import (
    build_semantic_house_description,
)
from modules.house_platform.application.port_in.generate_house_platform_embeddings_port import (
    GenerateHousePlatformEmbeddingsPort,
)
from modules.house_platform.application.port_out.embedding_port import EmbeddingPort
from modules.house_platform.application.port_out.house_platform_embedding_port import (
    HousePlatformEmbeddingReadPort,
    HousePlatformEmbeddingWritePort,
)


class GenerateHousePlatformEmbeddingsService(GenerateHousePlatformEmbeddingsPort):
    """전체 매물 임베딩을 생성하고 저장한다."""

    def __init__(
        self,
        reader: HousePlatformEmbeddingReadPort,
        writer: HousePlatformEmbeddingWritePort,
        embedder: EmbeddingPort,
    ):
        self.reader = reader
        self.writer = writer
        self.embedder = embedder

    async def execute(
        self, batch_size: int, concurrency: int
    ) -> HousePlatformEmbeddingResult:
        """전체 매물을 조회하고 임베딩을 저장한다."""
        sources = list(self.reader.fetch_all_sources())
        if not sources:
            return HousePlatformEmbeddingResult(
                total=0, embedded=0, saved=0, skipped=0, errors=[]
            )

        batches = _chunked(sources, batch_size)
        errors: list[str] = []
        embedded = 0
        saved = 0

        for i in range(0, len(batches), max(concurrency, 1)):
            chunk = batches[i : i + max(concurrency, 1)]
            results = await asyncio.gather(
                *(self._process_batch(batch) for batch in chunk),
                return_exceptions=True,
            )
            for result in results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                    continue
                batch_embedded, batch_saved = result
                embedded += batch_embedded
                saved += batch_saved

        return HousePlatformEmbeddingResult(
            total=len(sources),
            embedded=embedded,
            saved=saved,
            skipped=len(sources) - embedded,
            errors=errors,
        )

    async def _process_batch(
        self, batch: Sequence[HousePlatformSemanticSource]
    ) -> tuple[int, int]:
        embed_requests: list[EmbedRequest] = []
        desc_updates: dict[int, str | None] = {}

        for source in batch:
            if source.semantic_description:
                text = source.semantic_description
                desc_updates[source.house_platform_id] = None
            else:
                text = build_semantic_house_description(source)
                desc_updates[source.house_platform_id] = text
            embed_requests.append(
                EmbedRequest(record_id=source.house_platform_id, text=text)
            )

        embed_results = await self.embedder.embed(embed_requests)
        upserts: list[HousePlatformEmbeddingUpsert] = []
        for result in embed_results:
            upserts.append(
                HousePlatformEmbeddingUpsert(
                    house_platform_id=result.record_id,
                    embedding=result.vector,
                    semantic_description=desc_updates.get(result.record_id),
                )
            )

        saved = self.writer.upsert_embeddings(upserts)
        return len(embed_results), saved


def _chunked(
    items: Iterable[HousePlatformSemanticSource], size: int
) -> list[list[HousePlatformSemanticSource]]:
    if size <= 0:
        return [list(items)]
    chunks: list[list[HousePlatformSemanticSource]] = []
    buf: list[HousePlatformSemanticSource] = []
    for item in items:
        buf.append(item)
        if len(buf) >= size:
            chunks.append(buf)
            buf = []
    if buf:
        chunks.append(buf)
    return chunks
