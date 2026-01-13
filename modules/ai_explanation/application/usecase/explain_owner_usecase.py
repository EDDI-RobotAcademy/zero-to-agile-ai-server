from modules.ai_explanation.adapter.input.web.request.owner_request import OwnerExplanationRequest
from modules.ai_explanation.application.port.llm_port import LLMPort
from modules.ai_explanation.adapter.output.llm_adapter import LLMAdapter
from modules.ai_explanation.adapter.input.web.response.ai_response import AiResponse

class ExplainOwnerUseCase:
    def __init__(self, llm_port: LLMPort = None):
        self.llm_port = llm_port or LLMAdapter()

    def execute(self, request: OwnerExplanationRequest) -> AiResponse:
        explanation_text = self.llm_port.generate_owner_explanation(request)

        return AiResponse(message=explanation_text)