from fastapi import Depends

from infrastructure.db.postgres import get_db_session, SessionLocal
from modules.decision_context_signal_builder.application.usecase.build_decision_context_signal_usecase import \
    BuildDecisionContextSignalUseCase
from modules.finder_request.adapter.output.repository.finder_request_repository import (
    FinderRequestRepository,
)
from modules.house_platform.infrastructure.repository.house_platform_repository import (
    HousePlatformRepository,
)
from modules.observations.adapter.output.repository.student_recommendation_feature_observation_repository_impl import (
    StudentRecommendationFeatureObservationRepository,
)
from modules.recommendations.application.usecase.recommend_student_house import (
    RecommendStudentHouseService,
)
from modules.recommendations.application.usecase.recommend_student_house_mock import (
    RecommendStudentHouseMockService,
)
from modules.student_house_decision_policy.application.usecase.filter_candidate import (
    FilterCandidateService,
)
from modules.student_house_decision_policy.infrastructure.repository.house_platform_candidate_repository import (
    HousePlatformCandidateRepository,
)
from modules.student_house_decision_policy.infrastructure.repository.student_house_score_repository import (
    StudentHouseScoreRepository,
)


def get_filter_candidate_usecase(
    db_session=Depends(get_db_session),
) -> FilterCandidateService:
    """필터 후보 유스케이스 인스턴스를 생성한다."""
    finder_request_repo = FinderRequestRepository(db_session)
    observation_repo = StudentRecommendationFeatureObservationRepository(
        SessionLocal
    )
    candidate_repo = HousePlatformCandidateRepository()
    return FilterCandidateService(
        finder_request_repo,
        candidate_repo,
        observation_repo,
    )


def get_recommend_student_house_usecase(
    db_session=Depends(get_db_session),
) -> RecommendStudentHouseService:
    """추천 유스케이스 인스턴스를 생성한다."""
    finder_request_repo = FinderRequestRepository(db_session)
    house_platform_repo = HousePlatformRepository()
    observation_repo = StudentRecommendationFeatureObservationRepository(
        SessionLocal
    )
    score_repo = StudentHouseScoreRepository()
    return RecommendStudentHouseService(
        finder_request_repo=finder_request_repo,
        house_platform_repo=house_platform_repo,
        observation_repo=observation_repo,
        score_repo=score_repo,
    )


def get_recommend_student_house_mock_usecase(
    db_session=Depends(get_db_session),
) -> RecommendStudentHouseMockService:
    """추천 임시 응답 유스케이스 인스턴스를 생성한다."""
    finder_request_repo = FinderRequestRepository(db_session)
    house_platform_repo = HousePlatformRepository()
    observation_repo = StudentRecommendationFeatureObservationRepository(
        SessionLocal
    )
    score_repo = StudentHouseScoreRepository()
    return RecommendStudentHouseMockService(
        finder_request_repo=finder_request_repo,
        house_platform_repo=house_platform_repo,
        observation_repo=observation_repo,
        score_repo=score_repo,
    )

def get_build_decision_context_signal_usecase() -> BuildDecisionContextSignalUseCase:
    observation_repo = StudentRecommendationFeatureObservationRepository(
        SessionLocal
    )
    return BuildDecisionContextSignalUseCase(
        observation_repo=observation_repo
    )
