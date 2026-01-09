from __future__ import annotations

from typing import Sequence

from infrastructure.db.postgres import SessionLocal
from infrastructure.db.session_helper import open_session
from modules.observations.infrastructure.orm.student_recommendation_feature_observations_orm import (
    StudentRecommendationFeatureObservationORM,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    ObservationScoreSource,
)
from modules.student_house_decision_policy.application.port_out.observation_score_port import (
    ObservationScoreReadPort,
)


class ObservationScoreRepository(ObservationScoreReadPort):
    """관측 테이블 조회 구현체."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory or SessionLocal

    def fetch_by_version(
        self, observation_version: str | None
    ) -> Sequence[ObservationScoreSource]:
        session, generator = open_session(self._session_factory)
        try:
            query = session.query(StudentRecommendationFeatureObservationORM)
            if observation_version:
                query = query.filter(
                    StudentRecommendationFeatureObservationORM.observation_version
                    == observation_version
                )
            rows = query.all()
            return [self._to_source(row) for row in rows]
        finally:
            if generator:
                generator.close()
            else:
                session.close()

    @staticmethod
    def _to_source(
        row: StudentRecommendationFeatureObservationORM,
    ) -> ObservationScoreSource:
        return ObservationScoreSource(
            house_platform_id=row.house_platform_id,
            snapshot_id=row.snapshot_id,
            observation_version=row.observation_version,
            price_percentile=row.price_percentile,
            price_zscore=row.price_zscore,
            price_burden_nonlinear=row.price_burden_nonlinear,
            estimated_move_in_cost=row.estimated_move_in_cost,
            monthly_cost_est=row.monthly_cost_est,
            essential_option_coverage=row.essential_option_coverage,
            convenience_score=row.convenience_score,
            risk_probability_est=row.risk_probability_est,
            risk_severity_score=row.risk_severity_score,
            risk_nonlinear_penalty=row.risk_nonlinear_penalty,
            distance_to_school_min=row.distance_to_school_min,
            distance_percentile=row.distance_percentile,
            distance_nonlinear_score=row.distance_nonlinear_score,
        )
