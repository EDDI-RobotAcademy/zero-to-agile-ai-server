from pydantic import BaseModel, ConfigDict, Field


class RiskFlagRequest(BaseModel):
    severity: str = Field(..., description="리스크 심각도")
    message: str = Field(..., description="리스크 메시지")


class ListingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(..., description="매물 제목")
    description: str = Field(..., description="매물 설명")
    type: str = Field(..., description="매물 유형")
    images: list[str] = Field(..., description="이미지 URL 목록")
    sales_type: str = Field(..., alias="salesType", description="거래 유형")
    price: int = Field(..., description="가격")
    monthly_rent: int = Field(..., alias="monthlyRent", description="월세")
    manage_cost: int = Field(..., alias="manageCost", description="관리비")
    area: float = Field(..., description="면적")
    floor: int = Field(..., description="해당 층")
    all_floors: int = Field(..., alias="allFloors", description="전체 층수")
    has_elevator: bool = Field(..., alias="hasElevator", description="엘리베이터 여부")
    can_park: bool = Field(..., alias="canPark", description="주차 가능 여부")
    rank: int = Field(..., description="랭크")
    match_score: float = Field(..., alias="matchScore", description="매칭 점수")
    options: list[str] = Field(..., description="옵션 목록")
    ai_reasons: list[str] = Field(..., alias="aiReasons", description="AI 추천 이유")
    risk_level: str = Field(..., alias="riskLevel", description="리스크 레벨")
    risk_flags: list[RiskFlagRequest] = Field(
        ...,
        alias="riskFlags",
        description="리스크 플래그 목록",
    )
    risk_description: str = Field(
        ...,
        alias="riskDescription",
        description="리스크 설명",
    )


class ChatPromptRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    listing: ListingRequest = Field(..., description="매물 상세 정보")
    user_prompt: str = Field(..., alias="userPrompt", description="사용자 프롬프트")
    todo_descriptions: dict[str, str] | None = Field(
        default=None,
        alias="todoDescriptions",
        description="컬럼별 TODO 설명",
    )
