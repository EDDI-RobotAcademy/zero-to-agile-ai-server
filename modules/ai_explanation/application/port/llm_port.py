from abc import ABC, abstractmethod
from typing import List

from modules.ai_explanation.adapter.input.web.request.recommendation_explaination import (
    RecommendationItem,
)


class LLMPort(ABC):
    @abstractmethod
    def generate_reasons(
            self,
            recommendation: RecommendationItem,
            query_summary: str,
            tone: str = "formal",  # 파라미터 추가
    ) -> List[str]:
        raise NotImplementedError

    # explain_recommendation_usecase.py의 _generate_llm_reasons
    # def _generate_llm_reasons(
    #         self,
    #         item: RecommendationItem,
    #         query_summary: str,
    #         tone: ChatTone,  # 파라미터 추가
    # ) -> list[str]:
    #     if self._llm_port is None:
    #         try:
    #             self._llm_port = LLMAdapter()
    #         except Exception:
    #             return []
    #
    #     return self._llm_port.generate_reasons(
    #         item,
    #         query_summary,
    #         tone=tone.value  # tone 전달
    #     )
    #
    # # _collect_reasons에서 호출 시
    # generated = self._generate_llm_reasons(item, query_summary, tone)