from abc import ABC, abstractmethod
from typing import List

from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationItem,
)


class LLMPort(ABC):
    @abstractmethod
    def generate_reasons(
        self,
        recommendation: RecommendationItem,
        query_summary: str,
    ) -> List[str]:
        raise NotImplementedError