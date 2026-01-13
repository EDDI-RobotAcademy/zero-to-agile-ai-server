from dataclasses import dataclass
from typing import Optional

@dataclass
class UpdateUserDTO:
    user_id: int
    phone_number: Optional[str] = None
    university_name: Optional[str] = None
