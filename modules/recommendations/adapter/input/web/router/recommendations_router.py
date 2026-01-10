from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from modules.finder_request.adapter.input.web.dependencies import (
    get_finder_request_detail_usecase,
)
from modules.finder_request.application.usecase.get_finder_request_detail_usecase import (
    GetFinderRequestDetailUseCase,
)
from modules.recommendations.adapter.input.web.dependencies import (
    get_filter_candidate_usecase,
    get_recommend_student_house_mock_usecase,
    get_recommend_student_house_usecase,
)
from modules.recommendations.adapter.input.web.request.recommend_student_house_request import (
    RecommendStudentHouseRequest,
)
from modules.recommendations.adapter.input.web.response.recommend_student_house_response import (
    RecommendStudentHouseResponse,
)
from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseCommand,
    RecommendStudentHouseMockCommand,
    RecommendStudentHouseMockResponse,
)
from modules.recommendations.application.usecase.recommend_student_house import (
    RecommendStudentHouseService,
)
from modules.recommendations.application.usecase.recommend_student_house_mock import (
    RecommendStudentHouseMockService,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCommand,
)
from modules.student_house_decision_policy.application.usecase.filter_candidate import (
    FilterCandidateService,
)

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post(
    "/student-house",
    response_model=RecommendStudentHouseResponse,
    status_code=status.HTTP_200_OK,
    summary="학생 매물 추천 결과 조회",
)
def recommend_student_house(
    request: RecommendStudentHouseRequest,
    usecase: RecommendStudentHouseService = Depends(
        get_recommend_student_house_usecase
    ),
    filter_usecase: FilterCandidateService = Depends(
        get_filter_candidate_usecase
    ),
    mock_usecase: RecommendStudentHouseMockService = Depends(
        get_recommend_student_house_mock_usecase
    ),
    finder_request_usecase: GetFinderRequestDetailUseCase = Depends(
        get_finder_request_detail_usecase
    ),
) -> RecommendStudentHouseResponse:
    """매물 추천 결과를 반환한다."""
    finder_request = finder_request_usecase.execute(
        request.finder_request_id
    )
    if finder_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="finder_request not found",
        )
    filter_result = filter_usecase.execute(
        FilterCandidateCommand(finder_request_id=request.finder_request_id)
    )
    candidates = list(filter_result.candidates)
    candidate_ids = [candidate.house_platform_id for candidate in candidates]
    result = usecase.execute(
        RecommendStudentHouseCommand(
            finder_request_id=request.finder_request_id,
            candidate_house_platform_ids=candidate_ids,
        )
    )
    if result is None:
        mock_response = mock_usecase.execute(
            RecommendStudentHouseMockCommand(
                finder_request_id=request.finder_request_id,
                candidates=candidates,
            )
        )
        mock_result = mock_response.to_result()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=asdict(mock_result),
        )
    return RecommendStudentHouseResponse(**asdict(result))
