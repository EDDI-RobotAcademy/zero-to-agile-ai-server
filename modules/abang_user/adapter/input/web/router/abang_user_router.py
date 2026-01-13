from fastapi import APIRouter, Depends, HTTPException, status
from modules.abang_user.application.usecase.get_user_phone_usecase import GetUserPhoneUseCase
from modules.abang_user.application.usecase.update_user_usecase import UpdateUserUseCase
from modules.abang_user.application.dto.abang_phone_dto import AbangUserPhoneResponse
from modules.abang_user.application.dto.update_user_dto import UpdateUserDTO
from modules.abang_user.adapter.input.web.request.update_user_request import UpdateUserRequest
from modules.abang_user.adapter.input.web.response.user_response import UserResponse
from modules.abang_user.adapter.input.web.dependencies import get_get_user_phone_usecase, get_update_user_usecase
from modules.auth.adapter.input.auth_middleware import auth_required

router = APIRouter(prefix="/users", tags=["Abang User"])

@router.get(
    "/phone",
    response_model=AbangUserPhoneResponse,
    summary="사용자 전화번호 조회",
    description="로그인한 사용자의 전화번호를 조회합니다."
)
def get_user_phone(
    abang_user_id: int = Depends(auth_required),
    usecase: GetUserPhoneUseCase = Depends(get_get_user_phone_usecase)
):
    """
    로그인한 사용자의 전화번호를 조회합니다.
    """
    phone_number = usecase.execute(abang_user_id)
    
    return AbangUserPhoneResponse(phone_number=phone_number or "")

@router.put(
    "/update",
    response_model=UserResponse,
    summary="사용자 정보 수정",
    description="로그인한 사용자의 정보(전화번호, 대학교)를 수정합니다."
)
def update_user(
    request: UpdateUserRequest,
    abang_user_id: int = Depends(auth_required),
    usecase: UpdateUserUseCase = Depends(get_update_user_usecase)
):
    """
    사용자 정보를 수정합니다.
    
    - **phone_number**: 전화번호 (선택)
    - **university_name**: 대학교 이름 (선택)
    """
    # Request → DTO
    dto = UpdateUserDTO(
        user_id=abang_user_id,
        phone_number=request.phone_number,
        university_name=request.university_name
    )
    
    # UseCase 실행
    updated_user = usecase.execute(dto)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
        
    # Domain → Response
    return UserResponse(
        abang_user_id=updated_user.user_id,
        email=updated_user.email,
        nickname=updated_user.nickname,
        phone_number=updated_user.phone_number,
        university_name=updated_user.university_name,
        user_type=updated_user.user_type,
        created_at=updated_user.first_create_dt,
        updated_at=updated_user.last_update_dt
    )
