from fastapi import APIRouter, Depends

from modules.auth.adapter.input.auth_middleware import auth_required
from modules.owner_recommendation.adapter.input.web.dependencies import (
    get_owner_recommendation_usecase,
)
from modules.owner_recommendation.application.dto.owner_recommendation_dto import (
    OwnerRecommendationResponse,
)
from modules.owner_recommendation.application.usecase.get_owner_recommendation_usecase import (
    GetOwnerRecommendationUseCase,
)

router = APIRouter(prefix="/owner_recommendations", tags=["Owner Recommendation"])


@router.get(
    "/me",
    response_model=OwnerRecommendationResponse,
    summary="owner 추천 매물 조회",
    description="내 매물 중 임차인 요구서와 조건이 맞는 추천 결과를 조회합니다.",
)
def get_owner_recommendations(
    rent_margin: int = 5,
    abang_user_id: int = Depends(auth_required),
    usecase: GetOwnerRecommendationUseCase = Depends(
        get_owner_recommendation_usecase
    ),
):
    return usecase.execute(abang_user_id=abang_user_id, rent_margin=rent_margin)
