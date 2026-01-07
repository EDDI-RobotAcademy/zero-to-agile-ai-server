from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class SendMessageCreateRequest(BaseModel):
    house_platform_id: int
    finder_request_id: int
    message: Optional[str] = None

class SendMessageUpdateRequest(BaseModel):
    send_message_id: int
    message: str

class AcceptStatusUpdateRequest(BaseModel):
    send_message_id: int
    accept_type: str  # 'W', 'A' (Accepted), 'R' (Rejected)

class SendMessageResponse(BaseModel):
    send_message_id: int
    house_platform_id: int
    finder_request_id: int
    accept_type: Optional[str]
    message: Optional[str]
    receiver_id: int
    sender_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True