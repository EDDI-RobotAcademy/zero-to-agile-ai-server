from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from modules.finder_request.adapter.input.web.request.create_finder_request_request import CreateFinderRequestRequest
from modules.finder_request.adapter.input.web.request.edit_finder_request_request import EditFinderRequestRequest
from modules.finder_request.adapter.input.web.response.finder_request_response import FinderRequestResponse
from modules.auth.adapter.input.auth_middleware import auth_required
from modules.finder_request.adapter.input.web.dependencies import (
    get_create_finder_request_usecase,
    get_view_finder_requests_usecase,
    get_finder_request_detail_usecase,
    get_edit_finder_request_usecase,
    get_delete_finder_request_usecase
)
from modules.finder_request.application.usecase.create_finder_request_usecase import CreateFinderRequestUseCase
from modules.finder_request.application.usecase.view_finder_requests_usecase import ViewFinderRequestsUseCase
from modules.finder_request.application.usecase.get_finder_request_detail_usecase import GetFinderRequestDetailUseCase
from modules.finder_request.application.usecase.edit_finder_request_usecase import EditFinderRequestUseCase
from modules.finder_request.application.usecase.delete_finder_request_usecase import DeleteFinderRequestUseCase
from modules.finder_request.application.dto.finder_request_dto import CreateFinderRequestDTO


router = APIRouter(prefix="/requests", tags=["Finder Request"])


@router.post(
    "/create",
    response_model=FinderRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="임차인 요구서 생성",
    description="임차인이 자신의 조건이 담긴 요구서를 생성합니다."
)
def create_finder_request(
    request: CreateFinderRequestRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: CreateFinderRequestUseCase = Depends(get_create_finder_request_usecase)
):
    """
    임차인의 요구서를 생성합니다.
    
    - **abang_user_id**: 임차인 사용자 ID
    - **preferred_region**: 선호 지역
    - **price_type**: 가격 유형 (JEONSE, MONTHLY, MIXED)
    - **max_deposit**: 최대 보증금
    - **max_rent**: 최대 월세
    - **house_type**: 주거 형태
    - **additional_condition**: 추가 조건 (선택)
    """
    try:
        # Web Request DTO → Application DTO 변환
        dto = CreateFinderRequestDTO(
            abang_user_id=abang_user_id,
            preferred_region=request.preferred_region,
            price_type=request.price_type,
            max_deposit=request.max_deposit,
            max_rent=request.max_rent,
            house_type=request.house_type,
            additional_condition=request.additional_condition,
            university_name=request.university_name,
            status=request.status
        )
        
        # UseCase 실행
        result = usecase.execute(dto)
        
        # Application DTO → Web Response DTO 변환
        return FinderRequestResponse(
            finder_request_id=result.finder_request_id,
            abang_user_id=result.abang_user_id,
            preferred_region=result.preferred_region,
            price_type=result.price_type,
            max_deposit=result.max_deposit,
            max_rent=result.max_rent,
            status=result.status,
            house_type=result.house_type,
            additional_condition=result.additional_condition,
            university_name=result.university_name,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요구서 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/view",
    response_model=List[FinderRequestResponse],
    summary="임차인 요구서 목록 조회",
    description="특정 임차인의 요구서 목록을 조회합니다."
)
def view_finder_requests(
    abang_user_id: int = Depends(auth_required),
    usecase: ViewFinderRequestsUseCase = Depends(get_view_finder_requests_usecase)
):
    """
    임차인의 요구서 목록을 조회합니다.
    
    - **abang_user_id**: 임차인 사용자 ID (query parameter)
    """
    try:
        # UseCase 실행
        results = usecase.execute(abang_user_id)
        
        # Application DTO → Web Response DTO 변환
        return [
            FinderRequestResponse(
                finder_request_id=result.finder_request_id,
                abang_user_id=result.abang_user_id,
                preferred_region=result.preferred_region,
                price_type=result.price_type,
                max_deposit=result.max_deposit,
                max_rent=result.max_rent,
                status=result.status,
                house_type=result.house_type,
                additional_condition=result.additional_condition,
                university_name=result.university_name,
                created_at=result.created_at,
                updated_at=result.updated_at
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요구서 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get(
    "/view/{finder_request_id}",
    response_model=FinderRequestResponse,
    summary="임차인 요구서 상세 조회",
    description="특정 요구서의 상세 정보를 조회합니다."
)
def get_finder_request_detail(
    finder_request_id: int,
    usecase: GetFinderRequestDetailUseCase = Depends(get_finder_request_detail_usecase)
):
    """
    요구서의 상세 정보를 조회합니다.
    
    - **finder_request_id**: 요구서 ID (path parameter)
    """
    try:
        # UseCase 실행
        result = usecase.execute(finder_request_id)
        
        # 요구서가 없으면 404 반환
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"요구서 ID {finder_request_id}를 찾을 수 없습니다."
            )
        
        # Application DTO → Web Response DTO 변환
        return FinderRequestResponse(
            finder_request_id=result.finder_request_id,
            abang_user_id=result.abang_user_id,
            preferred_region=result.preferred_region,
            price_type=result.price_type,
            max_deposit=result.max_deposit,
            max_rent=result.max_rent,
            status=result.status,
            house_type=result.house_type,
            additional_condition=result.additional_condition,
            university_name=result.university_name,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요구서 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put(
    "/edit",
    response_model=FinderRequestResponse,
    summary="임차인 요구서 수정",
    description="임차인이 자신의 요구서를 수정합니다."
)
def edit_finder_request(
    request: EditFinderRequestRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: EditFinderRequestUseCase = Depends(get_edit_finder_request_usecase)
):
    """
    임차인의 요구서를 수정합니다.
    
    - **finder_request_id**: 수정할 요구서 ID
    - **abang_user_id**: 임차인 사용자 ID (권한 확인용)
    - **preferred_region**: 선호 지역 (선택)
    - **price_type**: 가격 유형 (선택)
    - **max_deposit**: 최대 보증금 (선택)
    - **max_rent**: 최대 월세 (선택)
    - **house_type**: 주거 형태 (선택)
    - **additional_condition**: 추가 조건 (선택)
    - **status**: 상태 (선택) - Y: 활성, N: 비활성
    """
    try:
        # UseCase 실행
        result = usecase.execute(
            finder_request_id=request.finder_request_id,
            abang_user_id=abang_user_id,
            preferred_region=request.preferred_region,
            price_type=request.price_type,
            max_deposit=request.max_deposit,
            max_rent=request.max_rent,
            house_type=request.house_type,
            additional_condition=request.additional_condition,
            university_name=request.university_name,
            status=request.status
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="요구서를 찾을 수 없거나 수정 권한이 없습니다."
            )
        
        # Application DTO → Web Response DTO 변환
        return FinderRequestResponse(
            finder_request_id=result.finder_request_id,
            abang_user_id=result.abang_user_id,
            preferred_region=result.preferred_region,
            price_type=result.price_type,
            max_deposit=result.max_deposit,
            max_rent=result.max_rent,
            status=result.status,
            house_type=result.house_type,
            additional_condition=result.additional_condition,
            university_name=result.university_name,
            created_at=result.created_at,
            updated_at=result.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요구서 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete(
    "/delete",
    summary="임차인 요구서 삭제",
    description="임차인이 자신의 요구서를 삭제합니다 (hard delete - 실제 DB row 삭제)."
)
def delete_finder_request(
    finder_request_id: int = Query(..., description="삭제할 요구서 ID", gt=0),
    abang_user_id: int = Depends(auth_required),
    usecase: DeleteFinderRequestUseCase = Depends(get_delete_finder_request_usecase)
):
    """
    임차인의 요구서를 삭제합니다 (hard delete - 실제 DB row 삭제).
    
    - **finder_request_id**: 삭제할 요구서 ID (query parameter)
    - **abang_user_id**: 임차인 사용자 ID (권한 확인용, query parameter)
    """
    try:
        # UseCase 실행
        success = usecase.execute(
            finder_request_id=finder_request_id,
            abang_user_id=abang_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="요구서를 찾을 수 없거나 삭제 권한이 없습니다."
            )
        
        return {"message": "요구서가 성공적으로 삭제되었습니다.", "finder_request_id": finder_request_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요구서 삭제 중 오류가 발생했습니다: {str(e)}"
        )
