from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationChatbotRequest,
)
from modules.chatbot.adapter.input.web.response.recommendation_chatbot import (
    RecommendationChatbotResponse,
)
from modules.chatbot.adapter.output.llm_adapter import LLMAdapter
from modules.chatbot.application.port.llm_port import LLMPort
from modules.chatbot.domain.tone import ChatTone


class ExplainRecommendationUseCase:
    def __init__(self, llm_port: LLMPort | None = None) -> None:
        self._llm_port = llm_port or LLMAdapter()

    def execute(
        self,
        request: RecommendationChatbotRequest,
    ) -> RecommendationChatbotResponse:
        explanation = self._build_explanation(request)
        return RecommendationChatbotResponse(message=explanation)

    def _build_explanation(self, request: RecommendationChatbotRequest) -> str:
        base_message = self._format_recommendations(request)
        if request.tone == ChatTone.CASUAL:
            return f"알려줄게! {base_message}"
        return f"안내드리겠습니다. {base_message}"

    def _format_recommendations(self, request: RecommendationChatbotRequest) -> str:
        if not request.recommendations:
            return f"요청 메시지를 확인했습니다: {request.message}"

        for item in request.recommendations:
            item.reasons = self._llm_port.generate_reasons(item, request.message or "")

        formatted_items = []
        for item in request.recommendations:
            reason_text = ", ".join(item.reasons) if item.reasons else "추천 이유 정보가 없습니다"
            formatted_items.append(f"{item.title} ({item.item_id}): {reason_text}")

        joined_items = " | ".join(formatted_items)
        return f"추천 매물 설명입니다: {joined_items}"