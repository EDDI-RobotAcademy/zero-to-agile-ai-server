from fastapi import APIRouter, Depends
from modules.university.application.usecase.get_universities_usecase import GetUniversitiesUseCase
from modules.university.application.dto.university_dto import UniversityListResponse
from modules.university.adapter.input.web.dependencies import get_get_universities_usecase

router = APIRouter(prefix="/universities", tags=["University"])

@router.get(
    "/names",
    response_model=UniversityListResponse,
    summary="모든 대학교 이름 조회",
    description="데이터베이스에 저장된 모든 대학교 이름을 가나다순으로 반환합니다."
)
def get_all_universities(
    usecase: GetUniversitiesUseCase = Depends(get_get_universities_usecase)
):
    universities = usecase.execute()
    return UniversityListResponse(universities=universities)
