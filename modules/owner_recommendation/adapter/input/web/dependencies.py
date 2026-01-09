from infrastructure.db.postgres import SessionLocal
from modules.owner_recommendation.adapter.output.owner_recommendation_repository_impl import (
    OwnerRecommendationRepositoryImpl,
)
from modules.owner_recommendation.application.usecase.get_owner_recommendation_usecase import (
    GetOwnerRecommendationUseCase,
)

_owner_recommendation_repo = None


def get_owner_recommendation_repository() -> OwnerRecommendationRepositoryImpl:
    global _owner_recommendation_repo
    if _owner_recommendation_repo is None:
        _owner_recommendation_repo = OwnerRecommendationRepositoryImpl(SessionLocal)
    return _owner_recommendation_repo


def get_owner_recommendation_usecase() -> GetOwnerRecommendationUseCase:
    return GetOwnerRecommendationUseCase(get_owner_recommendation_repository())
