from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Literal

class AcceptedProposalResponse(BaseModel):
    """
    수락된 제안 조회 응답 모델
    """
    send_message_id: int = Field(..., description="메시지 ID")
    message: Optional[str] = Field(None, description="메시지 내용")
    accepted_at: Optional[datetime] = Field(None, description="수락/수정 시각")
    target_type: Literal['HOUSE', 'REQUEST'] = Field(..., description="대상 유형 (HOUSE: 매물, REQUEST: 의뢰서)")
    target_data: Dict[str, Any] = Field(..., description="대상 상세 정보")
    
    class Config:
        from_attributes = True
