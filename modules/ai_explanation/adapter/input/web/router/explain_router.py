from fastapi import APIRouter
from modules.ai_explanation.adapter.input.web.request.owner_request import OwnerExplanationRequest
from modules.ai_explanation.adapter.input.web.response.owner_response import OwnerResponse
from modules.ai_explanation.application.usecase.explain_owner_usecase import ExplainOwnerUseCase

router = APIRouter(prefix="/explain", tags=["AI Explanation"])

@router.post("/owner", response_model=OwnerResponse, summary="임대인용 세입자 추천 이유 설명")
def explain_for_owner(request: OwnerExplanationRequest):
    """
    임대인이 추천받은 세입자 후보에 대해 AI 설명을 요청합니다.
    """
    usecase = ExplainOwnerUseCase()
    return usecase.execute(request)