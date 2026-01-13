from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    """
    사용자 정보 응답 모델
    """
    abang_user_id: int = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일")
    nickname: Optional[str] = Field(None, description="닉네임")
    phone_number: Optional[str] = Field(None, description="전화번호")
    university_name: Optional[str] = Field(None, description="대학교 이름")
    user_type: str = Field(..., description="사용자 유형")
    created_at: Optional[datetime] = Field(None, description="가입일")
    updated_at: Optional[datetime] = Field(None, description="최종 수정일")
    
    class Config:
        from_attributes = True
