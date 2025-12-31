from __future__ import annotations

import hashlib
import os
from typing import Sequence

import requests

class OpenAIEmbeddingAgent:
    """OpenAI text-embedding-3-small 호출 에이전트."""

    def __init__(self, api_key: str | None = None, use_dummy: bool = False):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.use_dummy = use_dummy or (self.api_key is None)
        self.model = "text-embedding-3-small"
        self.endpoint = "https://api.openai.com/v1/embeddings"

    def is_dummy(self) -> bool:
        return self.use_dummy

    async def embed_texts(self, texts: Sequence[str]) -> Sequence[list[float]]:
        if self.use_dummy:
            return [self._dummy_embed(text) for text in texts]
        resp = await _to_thread(
            requests_post,
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": texts},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]

    def _dummy_embed(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [((h[i % len(h)] - 128) / 128) for i in range(1536)]
        return vec


def requests_post(*args, **kwargs):
    """테스트 시 모킹을 쉽게 하기 위한 래퍼."""
    return requests.post(*args, **kwargs)


async def _to_thread(fn, *args, **kwargs):
    import asyncio

    return await asyncio.to_thread(fn, *args, **kwargs)
