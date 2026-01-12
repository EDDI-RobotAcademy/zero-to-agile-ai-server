from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ConvenienceObservationFeatures:
    필수_옵션_커버리지: float
    편의_점수: float

    def __post_init__(self):
        if not (0.0 <= self.필수_옵션_커버리지 <= 1.0):
            raise ValueError(f"필수 옵션 커버리지는 0 이상 1 이하이어야 합니다. 입력값: {self.필수_옵션_커버리지}")

        if not (0.0 <= self.편의_점수 <= 1.0):
            raise ValueError(f"편의 점수는 0 이상 1 이하이어야 합니다. 입력값: {self.편의_점수}")

    @classmethod
    def from_raw(cls, raw: Dict) -> "ConvenienceObservationFeatures":
        return cls(
            필수_옵션_커버리지=raw["essential_option_coverage"],
            편의_점수=raw["convenience_score"],
        )

    @classmethod
    def empty(cls) -> "ConvenienceObservationFeatures":
        """옵션이 없을 때 반환하는 기본 값"""
        return cls(필수_옵션_커버리지=0.0, 편의_점수=0.0)
