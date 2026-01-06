from pydantic import BaseModel, Field

class AbangUserPhoneResponse(BaseModel):
    phone_number: str = Field(..., description="사용자 전화번호 (11자리)", max_length=11)
