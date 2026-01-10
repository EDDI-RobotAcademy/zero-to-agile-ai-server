from modules.ai_explanation.application.port.llm_port import LLMPort
from modules.ai_explanation.adapter.output.llm_adapter import LLMAdapter
from modules.ai_explanation.adapter.input.web.response.ai_response import AiResponse
from modules.ai_explanation.domain.tone import ChatTone

class ExplainFinderUseCase:
    def __init__(self, llm_port: LLMPort = None):
        self.llm_port = llm_port or LLMAdapter()

    def execute(self, request) -> AiResponse:
        # Finder 전용 프롬프트 호출
        explanation = self.llm_port.generate_finder_explanation(
            items=request.recommendations,
            user_message=request.message,
            tone=ChatTone.FORMAL
        )
        return AiResponse(message=explanation)