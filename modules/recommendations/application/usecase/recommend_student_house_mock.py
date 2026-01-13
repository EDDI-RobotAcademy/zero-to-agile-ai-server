from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from modules.house_platform.domain.house_platform import HousePlatform
from modules.observations.domain.model.student_recommendation_feature_observation import (
    StudentRecommendationFeatureObservation,
    ObservationMetadata,
#    PriceObservationFeatures,
 #   DistanceObservationFeatures,
    RiskObservationFeatures,
    ConvenienceObservationFeatures,
    ObservationNotes,
)
from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseMockCommand,
    RecommendStudentHouseMockResponse,
)
from modules.recommendations.application.usecase.recommend_student_house import (
    RecommendStudentHouseService,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    StudentHouseScoreSummary,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)


class RecommendStudentHouseMockService(RecommendStudentHouseService):
    """추천 임시 응답을 생성한다."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._candidate_map: dict[int, Any] = {}

    def execute(
        self, command: RecommendStudentHouseMockCommand
    ) -> RecommendStudentHouseMockResponse:
        """후보 기반으로 임시 추천 응답을 생성한다."""
        policy = self.policy
        request = self.finder_request_repo.find_by_id(
            command.finder_request_id
        )
        query_context = (
            self._build_query_context(request, policy) if request else {}
        )
        self._candidate_map = {
            candidate.house_platform_id: candidate
            for candidate in command.candidates
        }

        sorted_candidates = sorted(
            command.candidates,
            key=lambda candidate: (
                candidate.deposit is None,
                candidate.deposit or 0,
            ),
        )

        recommended_candidates = sorted_candidates[: policy.top_k]
        rejected_candidates = list(reversed(sorted_candidates))[
            : policy.top_k
        ]
        recommended_ids = {
            candidate.house_platform_id
            for candidate in recommended_candidates
        }
        rejected_candidates = [
            candidate
            for candidate in rejected_candidates
            if candidate.house_platform_id not in recommended_ids
        ]

        recommended_items = self._build_ranked_items(
            self._build_rank_seed(
                recommended_candidates, base_score=80.0
            ),
            policy,
            decision_status="RECOMMENDED",
        )
        rejected_items = self._build_ranked_items(
            self._build_rank_seed(
                rejected_candidates, base_score=40.0
            ),
            policy,
            decision_status="REJECTED",
        )

        return RecommendStudentHouseMockResponse(
            finder_request_id=command.finder_request_id,
            recommended_top_k=recommended_items,
            rejected_top_k=rejected_items,
            total_candidates=len(command.candidates),
            query_context=query_context,
        )

    def _build_rank_seed(self, candidates: list[Any], base_score: float):
        ranked = []
        for index, candidate in enumerate(candidates):
            score = self._build_mock_score(
                candidate.house_platform_id,
                base_score=base_score - (index * 2.0),
            )
            ranked.append(
                (
                    candidate.house_platform_id,
                    score,
                    float(score.base_total_score),
                )
            )
        return ranked

    def _build_mock_score(
        self, house_platform_id: int, base_score: float
    ) -> StudentHouseScoreSummary:
        return StudentHouseScoreSummary(
            house_platform_id=house_platform_id,
            base_total_score=base_score,
            price_score=base_score,
            option_score=base_score,
            risk_score=base_score,
            distance_score=base_score,
            observation_version="mock",
            policy_version=self.policy.policy_version,
        )

    def _build_raw(self, house_platform_id: int) -> dict[str, Any]:
        raw = super()._build_raw(house_platform_id)
        if raw:
            return raw
        candidate = self._candidate_map.get(house_platform_id)
        house = HousePlatform(
            house_platform_id=house_platform_id,
            title=None,
            address=None,
            deposit=candidate.deposit if candidate else None,
            domain_id=None,
            rgst_no=None,
            sales_type=None,
            monthly_rent=candidate.monthly_rent if candidate else None,
            room_type=None,
            contract_area=None,
            exclusive_area=None,
            floor_no=None,
            all_floors=None,
            lat_lng=None,
            manage_cost=candidate.manage_cost if candidate else None,
            can_park=None,
            has_elevator=None,
            image_urls=None,
            pnu_cd=None,
            is_banned=None,
            residence_type=None,
            gu_nm=None,
            dong_nm=None,
            registered_at=None,
            crawled_at=None,
            snapshot_id=candidate.snapshot_id if candidate else None,
            abang_user_id=-1,
            created_at=None,
            updated_at=None,
        )
        raw = asdict(house)
        raw.pop("crawled_at", None)
        return raw

    def _fetch_observation(self, house_platform_id: int):
        observation = super()._fetch_observation(house_platform_id)
        if observation:
            return observation
        candidate = self._candidate_map.get(house_platform_id)
        monthly_rent = candidate.monthly_rent if candidate else 0
        manage_cost = candidate.manage_cost if candidate else 0
        deposit = candidate.deposit if candidate else 0
        estimated_move_in_cost = deposit + monthly_rent + manage_cost
        monthly_cost_est = monthly_rent + manage_cost
        snapshot_id = (
            candidate.snapshot_id if candidate else f"mock-{house_platform_id}"
        )
        return StudentRecommendationFeatureObservation(
            platform_id=house_platform_id,
            snapshot_id=snapshot_id,
            가격_관측치=PriceObservationFeatures(
                가격_백분위=0.5,
                가격_z점수=0.0,
                예상_입주비용=estimated_move_in_cost,
                월_비용_추정=monthly_cost_est,
                가격_부담_비선형=0.5,
            ),
            거리_관측치=DistanceObservationFeatures(
                학교까지_분=20.0,
                거리_백분위=0.5,
                거리_버킷="10_20",
                거리_비선형_점수=0.5,
            ),
            위험_관측치=RiskObservationFeatures(
                위험_사건_개수=0,
                위험_사건_유형=[],
                위험_확률_추정=0.1,
                위험_심각도_점수=0.1,
                위험_비선형_패널티=0.1,
            ),
            편의_관측치=ConvenienceObservationFeatures(
                필수_옵션_커버리지=0.5,
                편의_점수=0.5,
            ),
            관측_메모=ObservationNotes.empty(),
            메타데이터=ObservationMetadata(
                관측치_버전="mock",
                원본_데이터_버전="mock",
            ),
            calculated_at=datetime.now(timezone.utc),
        )
