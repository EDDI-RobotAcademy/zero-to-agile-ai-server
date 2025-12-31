from pydantic import BaseModel, Field


class RecommendStudentHouseRequest(BaseModel):
    finder_request_id: int = Field(..., description="요구서 ID", gt=0)
