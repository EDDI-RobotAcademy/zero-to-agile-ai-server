import json
import os
from typing import List

from openai import OpenAI

from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationItem,
)
from modules.chatbot.application.port.llm_port import LLMPort


class LLMAdapter(LLMPort):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._client = OpenAI(api_key=self._api_key)
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate_reasons(
        self,
        recommendation: RecommendationItem,
        query_summary: str,
    ) -> List[str]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a real estate assistant. Provide concise reasons "
                        "why a house listing is recommended based on the user's request. "
                        "Respond with a JSON array of short strings only."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"User request summary: {query_summary}\n"
                        f"Listing title: {recommendation.title}\n"
                        f"Listing id: {recommendation.item_id}\n"
                        "Return 2-4 recommendation reasons."
                    ),
                },
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content or "[]"
        reasons = self._parse_reason_list(content)
        if reasons:
            return reasons
        return ["추천 이유를 생성하지 못했습니다."]

    def _parse_reason_list(self, content: str) -> List[str]:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = None

        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]

        lines = [line.strip(" -•\t") for line in content.splitlines()]
        return [line for line in lines if line]