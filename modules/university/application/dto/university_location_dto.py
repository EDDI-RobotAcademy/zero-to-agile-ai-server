from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UniversityLocationDTO:
    """대학 위치 정보 DTO."""

    university_name: str
    campus: str
    lat: float
    lng: float
    region: str | None = None
    road_name_address: str | None = None
    jibun_address: str | None = None
