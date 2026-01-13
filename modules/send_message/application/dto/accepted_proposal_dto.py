from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class AcceptedProposalDTO:
    send_message_id: int
    message: Optional[str]
    accepted_at: Optional[datetime]
    target_type: str  # 'HOUSE' or 'REQUEST'
    target_data: Dict[str, Any]
