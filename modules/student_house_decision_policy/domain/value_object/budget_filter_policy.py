from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetFilterPolicy:
    """예산 기반 후보 선별 정책.

    코드 상에서 기본 여유율을 변경할 수 있도록 value object로 분리했다.
    """

    budget_margin_ratio: float = 0.1

    def clamp_budget(self, value: int | None) -> int | None:
        """예산 상한선에 여유율을 적용해 확장한다."""
        if value is None:
            return None
        if value <= 0:
            return None
        return int(value * (1.0 + self.budget_margin_ratio))
