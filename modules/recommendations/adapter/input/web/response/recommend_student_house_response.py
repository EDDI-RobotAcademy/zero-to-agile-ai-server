from typing import Any

from pydantic import BaseModel


class RecommendStudentHouseResponse(BaseModel):
    """추천 응답 DTO."""

    finder_request_id: int
    generated_at: str
    status: str
    detail: dict[str, Any] | None
    query_context: dict[str, Any]
    summary: dict[str, Any]
    recommended_top_k: list[dict[str, Any]]
    rejected_top_k: list[dict[str, Any]]
