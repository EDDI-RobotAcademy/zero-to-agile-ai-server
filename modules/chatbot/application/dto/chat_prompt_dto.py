from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class RiskFlagDto:
    severity: str
    message: str


@dataclass(frozen=True)
class ChatListingDto:
    title: str
    description: str
    type: str
    images: Sequence[str]
    sales_type: str
    price: int
    monthly_rent: int
    manage_cost: int
    area: float
    floor: int
    all_floors: int
    has_elevator: bool
    can_park: bool
    rank: int
    match_score: float
    options: Sequence[str]
    ai_reasons: Sequence[str]
    risk_level: str
    risk_flags: Sequence[RiskFlagDto]
    risk_description: str


@dataclass(frozen=True)
class ChatPromptRequestDto:
    listing: ChatListingDto
    user_prompt: str
    todo_descriptions: Mapping[str, str] | None


@dataclass(frozen=True)
class ChatPromptResponseDto:
    answer: str
