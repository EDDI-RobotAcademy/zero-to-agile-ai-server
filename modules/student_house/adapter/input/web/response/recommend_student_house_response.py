from typing import Any

from pydantic import BaseModel, Field


class RecommendStudentHouseResponse(BaseModel):
    request_id: str = Field(..., description="요청 식별자")
    query: dict = Field(default_factory=dict, description="요청 조건 요약")
    results: list[dict] = Field(default_factory=list, description="추천 결과")
    explain_message: str | None = Field(
        default=None, description="추천 설명 메시지"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="부가 정보"
    )
