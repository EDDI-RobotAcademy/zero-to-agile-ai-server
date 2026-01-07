from pydantic import BaseModel, Field


class HouseData(BaseModel):
    house_id: int
    title: str
    semantic_description: str | None = Field(None, description="직방 원본 설명")

    # student_house 관련 데이터
    school_distance: int | None = Field(None, description="학교 통학 시간(분)")
    price_percentile: float | None = Field(None, description="가격 백분위 (예: 20.5 -> 상위 20%)")
