from __future__ import annotations

from abc import ABC, abstractmethod


class UniversityLocationReadPort(ABC):
    """대학 위치 조회 포트."""

    @abstractmethod
    def get_location(self, university_name: str, campus: str | None = None) -> dict | None:
        """대학 좌표를 반환한다."""
        raise NotImplementedError
