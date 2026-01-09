from __future__ import annotations

from datetime import datetime, timezone

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    RefreshStudentHouseScoreCommand,
    RefreshStudentHouseScoreResult,
    StudentHouseScoreQuery,
)
from modules.student_house_decision_policy.application.factory.decision_score_calculator import (
    DecisionScoreCalculator,
)
from modules.student_house_decision_policy.application.port_in.refresh_student_house_score_port import (
    RefreshStudentHouseScorePort,
)
from modules.student_house_decision_policy.application.port_out.observation_score_port import (
    ObservationScoreReadPort,
)
from modules.student_house_decision_policy.application.port_out.student_house_score_port import (
    StudentHouseScorePort,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)


class RefreshStudentHouseScoreService(RefreshStudentHouseScorePort):
    """관측 버전에 맞춰 student_house 점수를 갱신한다."""

    def __init__(
        self,
        observation_repo: ObservationScoreReadPort,
        student_house_repo: StudentHouseScorePort,
        policy: DecisionPolicyConfig | None = None,
    ):
        self.observation_repo = observation_repo
        self.student_house_repo = student_house_repo
        self.policy = policy or DecisionPolicyConfig()

    def execute(
        self, command: RefreshStudentHouseScoreCommand
    ) -> RefreshStudentHouseScoreResult:
        policy = command.policy or self.policy
        calculator = DecisionScoreCalculator(policy)

        resolved_observation_version = (
            command.observation_version or _build_date_version()
        )
        # TODO: 관측 버전 관리 규칙이 확정되면 observation_version 매칭 로직을 고정한다.

        sources = list(
            self.observation_repo.fetch_by_version(
                command.observation_version
            )
        )
        # TODO: 관측 버전이 없는 경우 전체 스캔이 발생하므로 대상 범위를 제한하는 정책을 추가한다.

        processed = 0
        failed = 0
        for source in sources:
            try:
                record = calculator.calculate(
                    source,
                    observation_version=resolved_observation_version,
                    policy_version=policy.policy_version,
                )
                self.student_house_repo.upsert_score(record)
                processed += 1
            except Exception as exc:  # pragma: no cover - 예외 발생 시만 실행
                failed += 1
                self.student_house_repo.mark_failed(
                    source.house_platform_id, str(exc)
                )

        top_candidates = self.student_house_repo.fetch_top_k(
            StudentHouseScoreQuery(
                observation_version=resolved_observation_version,
                policy_version=policy.policy_version,
                threshold_base_total=policy.threshold_base_total,
                limit=policy.top_k,
            )
        )

        return RefreshStudentHouseScoreResult(
            observation_version=resolved_observation_version,
            policy_version=policy.policy_version,
            total_observations=len(sources),
            processed_count=processed,
            failed_count=failed,
            top_candidates=top_candidates,
        )


def _build_date_version() -> str:
    """임시 관측 버전 값을 만든다."""
    return datetime.now(timezone.utc).strftime("%Y%m%d")
