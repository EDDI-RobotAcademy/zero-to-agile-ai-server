from fastapi import APIRouter, Depends, HTTPException, status
from modules.abang_user.application.usecase.get_user_phone_usecase import GetUserPhoneUseCase
from modules.abang_user.application.dto.abang_phone_dto import AbangUserPhoneResponse
from modules.abang_user.adapter.input.web.dependencies import get_get_user_phone_usecase
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
