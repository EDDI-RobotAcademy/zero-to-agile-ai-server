from fastapi import APIRouter, Depends, HTTPException, status
from modules.abang_user.application.usecase.get_user_phone_usecase import GetUserPhoneUseCase
from modules.abang_user.application.dto.abang_phone_dto import AbangUserPhoneResponse
from modules.abang_user.adapter.input.web.dependencies import get_get_user_phone_usecase
from modules.auth.adapter.input.auth_middleware import auth_required

router = APIRouter(prefix="/users", tags=["Abang User"])

@router.get(
    "/{abang_user_id}/phone",
    response_model=AbangUserPhoneResponse,
    summary="사용자 전화번호 조회",
    description="특정 사용자의 전화번호를 조회합니다."
)
def get_user_phone(
    abang_user_id: int,
    request_user_id: int = Depends(auth_required),
    usecase: GetUserPhoneUseCase = Depends(get_get_user_phone_usecase)
):
    """
    사용자 ID로 전화번호를 조회합니다.
    
    - **abang_user_id**: 조회할 사용자 ID
    """
    # Optional: 본인 확인 로직? (기획에 따라 다름. 여기서는 임의의 user_id로 조회 요청이므로 허용하되, 인증된 사용자만 가능하게 함)
    
    phone_number = usecase.execute(abang_user_id)
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없거나 전화번호가 등록되지 않았습니다."
        )
        
    return AbangUserPhoneResponse(phone_number=phone_number)
