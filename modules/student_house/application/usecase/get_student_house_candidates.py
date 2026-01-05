from __future__ import annotations

from typing import Sequence

from modules.student_house.application.dto.student_house_dto import (
    StudentHouseCandidate,
    StudentHouseCandidateQuery,
    StudentHouseCandidateRaw,
)
from modules.student_house.application.factory.student_house_scoring_policy import (
    StudentHouseScoringPolicy,
)
from modules.student_house.application.port_in.get_student_house_candidates_port import (
    GetStudentHouseCandidatesPort,
)
from modules.student_house.application.port_out.student_house_repository_port import (
    StudentHouseRepositoryPort,
)
from modules.student_house.application.port_out.university_location_port import (
    UniversityLocationReadPort,
)


class GetStudentHouseCandidatesService(GetStudentHouseCandidatesPort):
    """추천 후보군 조회를 담당한다."""

    def __init__(
        self,
        repository: StudentHouseRepositoryPort,
        university_reader: UniversityLocationReadPort,
        policy: StudentHouseScoringPolicy | None = None,
    ):
        self.repository = repository
        self.university_reader = university_reader
        self.policy = policy or StudentHouseScoringPolicy.from_env()

    def get_high_score_candidates(
        self, query: StudentHouseCandidateQuery
    ) -> Sequence[StudentHouseCandidate]:
        """대학 위치를 기준으로 후보군을 계산한다."""
        university = self.university_reader.get_location(
            query.university_name, query.campus
        )
        if not university:
            return []

        lat = university.get("lat")
        lng = university.get("lng")
        if lat is None or lng is None:
            return []

        raw_candidates = self.repository.fetch_candidates(query)
        scored = [
            self._score_candidate(candidate, float(lat), float(lng))
            for candidate in raw_candidates
        ]
        scored = [item for item in scored if item is not None]
        scored.sort(key=lambda item: (-item.total_score, item.distance_km))
        return scored[: query.limit]

    def _score_candidate(
        self, candidate: StudentHouseCandidateRaw, lat: float, lng: float
    ) -> StudentHouseCandidate | None:
        """개별 후보의 거리 점수를 계산한다."""
        if candidate.lat is None or candidate.lng is None:
            distance_km = self.policy.distance_zero_score_km
            distance_score = 0.0
        else:
            distance_km = self.policy.calculate_distance_km(
                lat, lng, candidate.lat, candidate.lng
            )
            distance_score = self.policy.calculate_distance_score(distance_km)

        total_score = self.policy.calculate_total_score(
            candidate.base_total_score, distance_score
        )
        return StudentHouseCandidate(
            house_platform_id=candidate.house_platform_id,
            distance_km=round(distance_km, 3),
            distance_score=distance_score,
            base_total_score=candidate.base_total_score,
            total_score=total_score,
        )
