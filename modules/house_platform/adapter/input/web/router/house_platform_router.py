from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from modules.auth.adapter.input.auth_middleware import auth_required
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformCreateRequest,
    HousePlatformUpdateRequest,
    HousePlatformResponse
)
from modules.house_platform.application.usecase.create_house_platform_usecase import CreateHousePlatformUseCase
from modules.house_platform.application.usecase.get_house_platform_usecase import GetHousePlatformUseCase
from modules.house_platform.application.usecase.update_house_platform_usecase import UpdateHousePlatformUseCase
from modules.house_platform.application.usecase.delete_house_platform_usecase import DeleteHousePlatformUseCase
from modules.house_platform.adapter.input.web.dependencies import (
    get_create_house_platform_usecase,
    get_get_house_platform_usecase,
    get_update_house_platform_usecase,
    get_delete_house_platform_usecase
)

router = APIRouter(prefix="/house_platforms", tags=["House Platform"])

@router.post(
    "",
    response_model=HousePlatformResponse,
    status_code=status.HTTP_201_CREATED,
    summary="매물 등록",
    description="새로운 매물을 등록합니다."
)
def create_house_platform(
    request: HousePlatformCreateRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: CreateHousePlatformUseCase = Depends(get_create_house_platform_usecase)
):
    return usecase.execute(abang_user_id, request)

@router.get(
    "/me",
    response_model=List[HousePlatformResponse],
    summary="내 매물 목록 조회",
    description="현재 로그인한 사용자가 등록한 모든 매물을 조회합니다."
)
def get_my_house_platforms(
    abang_user_id: int = Depends(auth_required),
    usecase: GetHousePlatformUseCase = Depends(get_get_house_platform_usecase)
):
    return usecase.execute_get_all_by_user(abang_user_id)

@router.get(
    "/{house_platform_id}",
    response_model=HousePlatformResponse,
    summary="매물 상세 조회",
    description="특정 매물의 상세 정보를 조회합니다."
)
def get_house_platform(
    house_platform_id: int,
    abang_user_id: int = Depends(auth_required), # Assuming authentication is required even for viewing details for now, or to check ownership if needed in future logic
    usecase: GetHousePlatformUseCase = Depends(get_get_house_platform_usecase)
):
    # viewer_id 전달
    house = usecase.execute_get_by_id(house_platform_id, abang_user_id)
    if not house:
        raise HTTPException(status_code=404, detail="House platform not found")
    
    # 동적 속성(phone_number)을 Pydantic 모델에 반영하기 위해 dict로 변환하거나, 
    # Pydantic의 from_attributes가 객체의 속성을 읽어올 때 getattr를 사용하므로 
    # 동적으로 추가된 속성도 읽어올 수 있음.
    return house

@router.put(
    "/{house_platform_id}",
    response_model=HousePlatformResponse,
    summary="매물 수정",
    description="등록한 매물 정보를 수정합니다."
)
def update_house_platform(
    house_platform_id: int,
    request: HousePlatformUpdateRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: UpdateHousePlatformUseCase = Depends(get_update_house_platform_usecase)
):
    try:
        updated_house = usecase.execute(abang_user_id, house_platform_id, request)
        if not updated_house:
             raise HTTPException(status_code=404, detail="House platform not found")
        return updated_house
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete(
    "/{house_platform_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="매물 삭제",
    description="등록한 매물을 삭제합니다."
)
def delete_house_platform(
    house_platform_id: int,
    abang_user_id: int = Depends(auth_required),
    usecase: DeleteHousePlatformUseCase = Depends(get_delete_house_platform_usecase)
):
    try:
        success = usecase.execute(abang_user_id, house_platform_id)
        if not success:
             raise HTTPException(status_code=404, detail="House platform not found")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
