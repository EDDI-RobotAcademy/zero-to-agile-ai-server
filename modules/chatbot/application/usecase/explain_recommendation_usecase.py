from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationChatbotRequest,
    RecommendationItem,
)
from modules.chatbot.adapter.input.web.response.recommendation_chatbot import (
    RecommendationChatbotResponse,
)
from modules.chatbot.adapter.output.llm_adapter import LLMAdapter
from modules.chatbot.application.port.llm_port import LLMPort
from modules.chatbot.domain.tone import ChatTone


class ExplainRecommendationUseCase:
    def __init__(self, llm_port: LLMPort | None = None) -> None:
        self._llm_port = llm_port

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

        formatted_items = []
        for item in request.recommendations:
            reasons = self._collect_reasons(
                item,
                query_summary=request.message or "",
                tone=request.tone,
            )
            reason_text = ", ".join(reasons) if reasons else "추천 이유 정보가 없습니다"
            formatted_items.append(f"{item.title} ({item.item_id}): {reason_text}")
        joined_items = " | ".join(formatted_items)
        return f"추천 매물 설명입니다: {joined_items}"

    def _collect_reasons(
        self,
        item: RecommendationItem,
        query_summary: str,
        tone: ChatTone,
    ) -> list[str]:
        """house_platform에서 제공한 이유/요약을 우선 활용한다."""
        reasons: list[str] = [
            reason for reason in item.reasons if reason
        ]

        if item.semantic_description:
            reasons.append(item.semantic_description)

        derived = self._derive_reasons_from_metadata(item, tone)
        if derived:
            reasons.extend(derived)

        if reasons:
            return self._deduplicate_reasons(reasons)

        generated = self._generate_llm_reasons(item, query_summary)
        return self._deduplicate_reasons(generated) if generated else []

    def _generate_llm_reasons(
        self,
        item: RecommendationItem,
        query_summary: str,
    ) -> list[str]:
        if self._llm_port is None:
            try:
                self._llm_port = LLMAdapter()
            except Exception:
                return []

        return self._llm_port.generate_reasons(item, query_summary)

    def _deduplicate_reasons(self, reasons: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for reason in reasons:
            if reason not in seen:
                unique.append(reason)
                seen.add(reason)
        return unique

    def _derive_reasons_from_metadata(
        self,
        item: RecommendationItem,
        tone: ChatTone,
    ) -> list[str]:
        """house_platform이 내려준 매물 필드를 활용해 기본 설명을 만든다."""
        reasons: list[str] = []

        if item.address and item.room_type:
            reasons.append(
                self._select_tone(
                    formal=f"{item.address}에 위치한 {item.room_type} 매물입니다.",
                    casual=f"{item.address}에 있는 {item.room_type} 집이야.",
                    tone=tone,
                )
            )
        elif item.address:
            reasons.append(
                self._select_tone(
                    formal=f"{item.address}에 위치한 매물입니다.",
                    casual=f"{item.address}에 있는 집이야.",
                    tone=tone,
                )
            )
        elif item.room_type:
            reasons.append(
                self._select_tone(
                    formal=f"{item.room_type} 유형 매물입니다.",
                    casual=f"{item.room_type} 타입 집이야.",
                    tone=tone,
                )
            )

        price_parts: list[str] = []
        if item.deposit is not None:
            price_parts.append(f"보증금 {item.deposit}만원")
        if item.monthly_rent is not None:
            price_parts.append(f"월세 {item.monthly_rent}만원")
        if item.manage_cost is not None:
            price_parts.append(f"관리비 {item.manage_cost}만원")
        if price_parts:
            reasons.append(
                self._select_tone(
                    formal=", ".join(price_parts) + " 조건입니다.",
                    casual=", ".join(price_parts) + " 조건이야.",
                    tone=tone,
                )
            )

        if item.near_transport is True:
            reasons.append(
                self._select_tone(
                    formal="대중교통 접근성이 좋아 통학/출퇴근이 편리합니다.",
                    casual="대중교통 접근성이 좋아서 통학/출퇴근이 편해.",
                    tone=tone,
                )
            )
        if item.near_mart is True:
            reasons.append(
                self._select_tone(
                    formal="근처에 편의시설이 있어 생활이 편리합니다.",
                    casual="근처에 편의시설 있어서 살기 편해.",
                    tone=tone,
                )
            )
        if item.near_univ is True:
            reasons.append(
                self._select_tone(
                    formal="학교와 가까워 통학에 유리합니다.",
                    casual="학교랑 가까워서 통학하기 좋아.",
                    tone=tone,
                )
            )

        if item.can_park is True:
            reasons.append(
                self._select_tone(
                    formal="주차가 가능해 차량 보유 시 편리합니다.",
                    casual="주차가 돼서 차 있어도 편해.",
                    tone=tone,
                )
            )
        if item.has_elevator is True:
            reasons.append(
                self._select_tone(
                    formal="엘리베이터가 있어 짐 이동이 수월합니다.",
                    casual="엘리베이터 있어서 짐 옮기기 편해.",
                    tone=tone,
                )
            )

        if item.built_in:
            reasons.append(
                self._select_tone(
                    formal=f"옵션: {', '.join(item.built_in)}",
                    casual=f"옵션은 {', '.join(item.built_in)}야.",
                    tone=tone,
                )
            )

        return reasons

    def _select_tone(self, formal: str, casual: str, tone: ChatTone) -> str:
        return casual if tone == ChatTone.CASUAL else formal