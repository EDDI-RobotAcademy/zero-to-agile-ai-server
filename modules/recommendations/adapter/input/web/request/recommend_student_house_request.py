from pydantic import BaseModel


class RecommendStudentHouseRequest(BaseModel):
    """추천 요청 DTO."""

    finder_request_id: int
