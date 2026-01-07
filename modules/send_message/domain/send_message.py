from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SendMessage:
    send_message_id: Optional[int]
    house_platform_id: int
    finder_request_id: int
    accept_type: str
    message: Optional[str]
    receiver_id: int
    sender_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
