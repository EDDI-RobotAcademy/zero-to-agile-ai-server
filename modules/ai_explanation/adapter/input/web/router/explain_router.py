from fastapi import APIRouter
from modules.ai_explanation.adapter.input.web.request.finder_request import FinderExplanationRequest
from modules.ai_explanation.adapter.input.web.request.owner_request import OwnerExplanationRequest
from modules.ai_explanation.adapter.input.web.response.ai_response import AiResponse
from modules.ai_explanation.application.usecase.explain_finder_usecase import ExplainFinderUseCase
from modules.ai_explanation.application.usecase.explain_owner_usecase import ExplainOwnerUseCase

# 태그와 prefix를 여기서 한 번에 관리
router = APIRouter(prefix="/explain", tags=["AI Explanation"])

@router.post("/finder", response_model=AiResponse, summary="임차인용 매물 추천 설명")
def explain_for_finder(request: FinderExplanationRequest):
    """
    임차인이 추천받은 매물에 대해 AI 설명을 요청합니다.
    """
    usecase = ExplainFinderUseCase()
    return usecase.execute(request)

@router.post("/owner", response_model=AiResponse, summary="임대인용 세입자 추천 설명")
def explain_for_owner(request: OwnerExplanationRequest):
    """
    임대인이 추천받은 세입자 후보에 대해 AI 설명을 요청합니다.
    """
    usecase = ExplainOwnerUseCase()
    return usecase.execute(request)