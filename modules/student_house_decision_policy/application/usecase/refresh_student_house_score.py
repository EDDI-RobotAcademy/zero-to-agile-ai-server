from __future__ import annotations

from datetime import datetime, timezone

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    ObservationScoreSource,
    RefreshStudentHouseScoreCommand,
    RefreshStudentHouseScoreResult,
)
from modules.student_house_decision_policy.application.factory.decision_score_calculator import (
    DecisionScoreCalculator,
)
from modules.student_house_decision_policy.application.port_in.refresh_student_house_score_port import (
    RefreshStudentHouseScorePort,
)
from modules.student_house_decision_policy.application.port_out.student_house_score_port import (
    StudentHouseScorePort,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCriteria,
)
from modules.student_house_decision_policy.application.port_out.house_platform_candidate_port import (
    HousePlatformCandidateReadPort,
)
from modules.observations.application.port.observation_repository_port import (
    ObservationRepositoryPort,
)
from modules.observations.application.port.price_observation_repository_port import (
    PriceObservationRepositoryPort,
)
from modules.observations.application.port.distance_observation_repository_port import (
    DistanceObservationRepositoryPort,
)
from modules.university.application.port.university_repository_port import (
    UniversityRepositoryPort,
)
from modules.observations.domain.model.distance_feature_observation import (
    DistanceFeatureObservation,
)


class RefreshStudentHouseScoreService(RefreshStudentHouseScorePort):
    """관측 버전에 맞춰 student_house 점수를 갱신한다."""

    def __init__(
        self,
        house_platform_repo: HousePlatformCandidateReadPort,
        feature_observation_repo: ObservationRepositoryPort,
        price_observation_repo: PriceObservationRepositoryPort,
        distance_observation_repo: DistanceObservationRepositoryPort,
        university_repo: UniversityRepositoryPort,
        student_house_repo: StudentHouseScorePort,
        policy: DecisionPolicyConfig | None = None,
    ):
        self.house_platform_repo = house_platform_repo
        self.feature_observation_repo = feature_observation_repo
        self.price_observation_repo = price_observation_repo
        self.distance_observation_repo = distance_observation_repo
        self.university_repo = university_repo
        self.student_house_repo = student_house_repo
        self.policy = policy or DecisionPolicyConfig()

    def execute(
        self, command: RefreshStudentHouseScoreCommand
    ) -> RefreshStudentHouseScoreResult:
        policy = command.policy or self.policy
        calculator = DecisionScoreCalculator(policy)

        # TODO: 관측 버전 관리 규칙이 확정되면 매칭 규칙을 고정한다.

        unique_university_ids = set(
            self.university_repo.get_unique_university_locations()
        )

        candidates = self.house_platform_repo.fetch_candidates(
            FilterCandidateCriteria(
                max_deposit_limit=None,
                max_rent_limit=None,
                budget_margin_ratio=0.0,
            ),
            limit=None,
        )
        # TODO: 대상 범위를 제한하는 정책이 확정되면 후보 조회 범위를 조정한다.

        processed = 0
        failed = 0
        for candidate in candidates:
            try:
                source = self._build_score_source(
                    candidate.house_platform_id,
                    candidate.snapshot_id,
                    unique_university_ids,
                    command.observation_version,
                )
                record = calculator.calculate(
                    source,
                    observation_version=command.observation_version,
                    policy_version=policy.policy_version,
                )
                self.student_house_repo.upsert_score(record)
                processed += 1
            except Exception as exc:  # pragma: no cover - 예외 발생 시만 실행
                failed += 1
                self.student_house_repo.mark_failed(
                    candidate.house_platform_id, str(exc)
                )

        return RefreshStudentHouseScoreResult(
            observation_version=command.observation_version,
            policy_version=policy.policy_version,
            total_observations=len(candidates),
            processed_count=processed,
            failed_count=failed,
        )

    def _build_score_source(
        self,
        house_platform_id: int,
        snapshot_id: str | None,
        unique_university_ids: set[int],
        expected_observation_version: str | None,
    ) -> ObservationScoreSource:
        """관측 포트를 조합해 점수 산출용 관측치를 만든다."""
        feature = self._find_latest_feature(house_platform_id)
        observation_version = expected_observation_version
        if feature:
            snapshot_id = feature.snapshot_id
            observation_version = feature.메타데이터.관측치_버전
            if (
                expected_observation_version
                and feature.메타데이터.관측치_버전
                != expected_observation_version
            ):
                raise ValueError("관측 버전이 일치하지 않습니다.")
        else:
            # TODO: feature 관측치가 없을 때 snapshot/버전 정책을 확정한다.
            observation_version = expected_observation_version

        price = self.price_observation_repo.get_by_house_platform_id(
            house_platform_id
        )
        if not price:
            raise ValueError("price 관측치가 존재하지 않습니다.")

        distances = (
            self.distance_observation_repo.get_bulk_by_house_platform_id(
                house_platform_id
            )
        )
        if unique_university_ids:
            distances = [
                item
                for item in distances
                if item.university_id in unique_university_ids
            ]
        if not distances:
            raise ValueError("distance 관측치가 존재하지 않습니다.")

        distance_summary = _average_distance(distances)
        # TODO: 코호트/대표 대학 정책이 확정되면 평균 산정 대신 정책 기반 대표값을 사용한다.

        return ObservationScoreSource(
            house_platform_id=house_platform_id,
            snapshot_id=snapshot_id,
            observation_version=observation_version,
            price_percentile=price.가격_백분위,
            price_zscore=price.가격_z점수,
            price_burden_nonlinear=price.가격_부담_비선형,
            estimated_move_in_cost=int(price.예상_입주비용),
            monthly_cost_est=int(price.월_비용_추정),
            essential_option_coverage=(
                feature.편의_관측치.필수_옵션_커버리지
                if feature
                else None
            ),
            convenience_score=feature.편의_관측치.편의_점수 if feature else None,
            risk_probability_est=(
                feature.위험_관측치.위험_확률_추정 if feature else None
            ),
            risk_severity_score=(
                feature.위험_관측치.위험_심각도_점수 if feature else None
            ),
            risk_nonlinear_penalty=(
                feature.위험_관측치.위험_비선형_패널티 if feature else None
            ),
            distance_to_school_min=distance_summary[0],
            distance_percentile=distance_summary[1],
            distance_nonlinear_score=distance_summary[2],
        )

    def _find_latest_feature(self, house_platform_id: int):
        if not hasattr(self.feature_observation_repo, "find_latest_by_house_id"):
            raise AttributeError("feature 관측 저장소가 없습니다.")
        return self.feature_observation_repo.find_latest_by_house_id(
            house_platform_id
        )


def _average_distance(
    distances: list[DistanceFeatureObservation],
) -> tuple[float, float, float]:
    """거리 관측치를 평균으로 요약한다."""
    count = max(len(distances), 1)
    minutes = sum(item.학교까지_분 for item in distances) / count
    percentile = sum(item.거리_백분위 for item in distances) / count
    nonlinear = sum(item.거리_비선형_점수 for item in distances) / count
    return float(minutes), float(percentile), float(nonlinear)
