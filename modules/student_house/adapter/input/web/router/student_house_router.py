from fastapi import APIRouter, Depends, HTTPException, status

from infrastructure.db.postgres import get_db_session
from infrastructure.external.embedding_agent import OpenAIEmbeddingAgent
from modules.chatbot.adapter.input.web.request.recommendation_chatbot import (
    RecommendationChatbotRequest,
    RecommendationItem,
)
from modules.chatbot.application.usecase.explain_recommendation_usecase import (
    ExplainRecommendationUseCase,
)
from modules.chatbot.domain.tone import ChatTone
from modules.finder_request.adapter.output.repository.finder_request_repository import (
    FinderRequestRepository,
)
from modules.finder_request.infrastructure.repository.finder_request_embedding_repository import (
    FinderRequestEmbeddingRepository,
)
from modules.student_house.adapter.input.web.request.recommend_student_house_request import (
    RecommendStudentHouseRequest,
)
from modules.student_house.adapter.input.web.response.recommend_student_house_response import (
    RecommendStudentHouseResponse,
)
from modules.student_house.adapter.output.recommendation_agent import (
    StudentHouseRecommendationAgent,
)
from modules.student_house.application.usecase.recommend_student_house_for_finder_request import (
    RecommendStudentHouseUseCase,
)
from modules.student_house.infrastructure.repository.student_house_embedding_search_repository import (
    StudentHouseEmbeddingSearchRepository,
)
from modules.student_house.infrastructure.repository.student_house_search_repository import (
    StudentHouseSearchRepository,
)

router = APIRouter(prefix="/student_house", tags=["student_house"])


@router.post(
    "/recommend",
    response_model=RecommendStudentHouseResponse,
    status_code=status.HTTP_200_OK,
)
def recommend_student_house(
    request: RecommendStudentHouseRequest,
    db=Depends(get_db_session),
) -> RecommendStudentHouseResponse:
    finder_request_repo = FinderRequestRepository(db)
    embedding_repo = FinderRequestEmbeddingRepository()
    search_repo = StudentHouseSearchRepository()
    vector_repo = StudentHouseEmbeddingSearchRepository()
    embedder = OpenAIEmbeddingAgent()

    usecase = RecommendStudentHouseUseCase(
        finder_request_repo,
        embedding_repo,
        search_repo,
        vector_repo,
        embedder,
    )
    agent = StudentHouseRecommendationAgent(usecase)
    finder_request = finder_request_repo.find_by_id(request.finder_request_id)
    result = agent.run(finder_request)

    if result.get("request_id") is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="finder_request not found",
        )

    explain_message = _build_explain_message(result)

    return RecommendStudentHouseResponse(
        request_id=result.get("request_id", ""),
        query=result.get("query", {}),
        results=result.get("results", []),
        explain_message=explain_message,
        metadata={"explain_count": len(result.get("results", []))},
    )


def _build_explain_message(result: dict) -> str | None:
    recommendations = []
    for item in result.get("results", []):
        house = item.get("house", {}) or {}
        recommendations.append(
            RecommendationItem(
                item_id=house.get("house_platform_id", 0),
                title=house.get("title") or "추천 매물",
                address=house.get("address"),
                room_type=house.get("room_type"),
                residence_type=house.get("residence_type"),
                deposit=house.get("deposit"),
                monthly_rent=house.get("monthly_rent"),
                manage_cost=house.get("manage_cost"),
                contract_area=house.get("contract_area"),
                exclusive_area=house.get("exclusive_area"),
                floor_no=house.get("floor"),
                all_floors=house.get("all_floors"),
                can_park=house.get("can_park"),
                has_elevator=house.get("has_elevator"),
                built_in=house.get("built_in"),
                near_univ=house.get("near_univ"),
                near_transport=house.get("near_transport"),
                near_mart=house.get("near_mart"),
                management_included=house.get("management_included"),
                management_excluded=house.get("management_excluded"),
                semantic_description=None,
                reasons=item.get("why_recommended", []),
            )
        )

    if not recommendations:
        return None

    request = RecommendationChatbotRequest(
        tone=ChatTone.FORMAL,
        message=None,
        recommendations=recommendations,
    )
    usecase = ExplainRecommendationUseCase()
    response = usecase.execute(request)
    return response.message
