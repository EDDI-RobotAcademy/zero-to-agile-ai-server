from pydantic import BaseModel
from typing import List

class UniversityListResponse(BaseModel):
    universities: List[str]
