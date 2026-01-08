from pydantic import BaseModel, Field
from typing import Optional

class UpdateUserRequest(BaseModel):
    """
    사용자 정보 수정 요청 모델
    """
    phone_number: Optional[str] = Field(None, description="전화번호 (하이픈 없이 11자리 권장)", max_length=11)
    university_name: Optional[str] = Field(None, description="대학교 이름", max_length=50)
