from modules.ai_explanation.application.port.llm_port import LLMPort
from modules.ai_explanation.adapter.output.llm_adapter import LLMAdapter
from modules.ai_explanation.adapter.input.web.response.owner_response import OwnerResponse
from modules.ai_explanation.adapter.input.web.request.owner_request import OwnerExplanationRequest

class ExplainOwnerUseCase:
    def __init__(self, llm_port: LLMPort = None):
        self.llm_port = llm_port or LLMAdapter()

    def execute(self, request: OwnerExplanationRequest) -> OwnerResponse:
        explanation_text = self.llm_port.generate_owner_explanation(request)

        return OwnerResponse(message=explanation_text)