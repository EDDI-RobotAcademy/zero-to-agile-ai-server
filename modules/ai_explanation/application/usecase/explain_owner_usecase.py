from modules.ai_explanation.application.port.llm_port import LLMPort
from modules.ai_explanation.adapter.output.llm_adapter import LLMAdapter
from modules.ai_explanation.adapter.input.web.response.ai_response import AiResponse

class ExplainOwnerUseCase:
    def __init__(self, llm_port: LLMPort = None):
        self.llm_port = llm_port or LLMAdapter()

    def execute(self, request) -> AiResponse:
        # Owner 전용 프롬프트 호출
        explanation = self.llm_port.generate_owner_explanation(
            house=request.my_house,
            tenant=request.candidate,
            tone=request.tone
        )
        return AiResponse(message=explanation)