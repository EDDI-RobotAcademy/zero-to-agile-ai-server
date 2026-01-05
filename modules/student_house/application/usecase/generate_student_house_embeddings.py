from __future__ import annotations

import asyncio
from typing import Iterable, Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseEmbeddingResult,
    StudentHouseEmbeddingUpsert,
    StudentHouseSemanticSource,
)
from modules.student_house.application.factory.student_house_semantic_factory import (
    build_student_house_description,
)
from modules.student_house.application.port_in.generate_student_house_embeddings_port import (
    GenerateStudentHouseEmbeddingsPort,
)
from modules.student_house.application.port_out.student_house_embedding_port import (
    StudentHouseEmbeddingReadPort,
    StudentHouseEmbeddingWritePort,
)


class GenerateStudentHouseEmbeddingsService(GenerateStudentHouseEmbeddingsPort):
    """student_house 임베딩 생성/저장을 담당한다."""

    def __init__(
        self,
        reader: StudentHouseEmbeddingReadPort,
        writer: StudentHouseEmbeddingWritePort,
        embedder,
    ):
        self.reader = reader
        self.writer = writer
        self.embedder = embedder

    async def execute(
        self, batch_size: int, concurrency: int
    ) -> StudentHouseEmbeddingResult:
        """전체 student_house 임베딩을 생성/저장한다."""
        sources = list(self.reader.fetch_all_sources())
        if not sources:
            return StudentHouseEmbeddingResult(
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

        return StudentHouseEmbeddingResult(
            total=len(sources),
            embedded=embedded,
            saved=saved,
            skipped=len(sources) - embedded,
            errors=errors,
        )

    async def _process_batch(
        self, batch: Sequence[StudentHouseSemanticSource]
    ) -> tuple[int, int]:
        texts: list[str] = []
        student_house_ids: list[int] = []
        desc_updates: dict[int, str | None] = {}

        for source in batch:
            if source.semantic_description:
                text = source.semantic_description
                desc_updates[source.student_house_id] = None
            else:
                text = build_student_house_description(source)
                desc_updates[source.student_house_id] = text
            texts.append(text)
            student_house_ids.append(source.student_house_id)

        vectors = await self.embedder.embed_texts(texts)
        upserts: list[StudentHouseEmbeddingUpsert] = []
        for student_house_id, vector in zip(student_house_ids, vectors):
            upserts.append(
                StudentHouseEmbeddingUpsert(
                    student_house_id=student_house_id,
                    embedding=vector,
                    semantic_description=desc_updates.get(student_house_id),
                )
            )

        saved = self.writer.upsert_embeddings(upserts)
        return len(vectors), saved


def _chunked(
    items: Iterable[StudentHouseSemanticSource], size: int
) -> list[list[StudentHouseSemanticSource]]:
    if size <= 0:
        return [list(items)]
    chunks: list[list[StudentHouseSemanticSource]] = []
    buf: list[StudentHouseSemanticSource] = []
    for item in items:
        buf.append(item)
        if len(buf) >= size:
            chunks.append(buf)
            buf = []
    if buf:
        chunks.append(buf)
    return chunks
