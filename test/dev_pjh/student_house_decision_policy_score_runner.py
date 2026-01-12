"""student_house_decision_policy 스코어 갱신 러너."""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    RefreshStudentHouseScoreCommand,
)
from modules.student_house_decision_policy.application.usecase.refresh_student_house_score import (
    RefreshStudentHouseScoreService,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)
from infrastructure.db.postgres import SessionLocal
from infrastructure.db.session_helper import open_session
from modules.observations.adapter.output.repository.student_recommendation_feature_observation_repository_impl import (
    StudentRecommendationFeatureObservationRepository,
)
from modules.observations.adapter.output.repository.student_recommendtation_price_observation_repository_impl import (
    StudentRecommendationPriceObservationRepository,
)
from modules.observations.adapter.output.repository.student_recommendation_distance_observation_repository_impl import (
    StudentRecommendationDistanceObservationRepository,
)
from modules.student_house_decision_policy.infrastructure.repository.house_platform_candidate_repository import (
    HousePlatformCandidateRepository,
)
from modules.student_house_decision_policy.infrastructure.repository.student_house_score_repository import (
    StudentHouseScoreRepository,
)
from modules.university.adapter.output.university_repository import (
    UniversityRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observation-version",
        type=str,
        default=None,
        help="관측 버전(없으면 전체 조회 + 날짜 버전 사용)",
    )
    parser.add_argument(
        "--policy-version",
        type=str,
        default="v1",
        help="정책 버전",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=50.0,
        help="추천 기준 점수",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="상위 후보 개수",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    policy = DecisionPolicyConfig(
        threshold_base_total=args.threshold,
        top_k=args.top_k,
        policy_version=args.policy_version,
    )
    session, generator = open_session(SessionLocal)
    try:
        house_platform_repo = HousePlatformCandidateRepository()
        feature_repo = StudentRecommendationFeatureObservationRepository(
            SessionLocal
        )
        price_repo = StudentRecommendationPriceObservationRepository(
            session
        )
        distance_repo = StudentRecommendationDistanceObservationRepository(
            session
        )
        university_repo = UniversityRepository(SessionLocal)
        student_house_repo = StudentHouseScoreRepository()

        usecase = RefreshStudentHouseScoreService(
            house_platform_repo=house_platform_repo,
            feature_observation_repo=feature_repo,
            price_observation_repo=price_repo,
            distance_observation_repo=distance_repo,
            university_repo=university_repo,
            student_house_repo=student_house_repo,
            policy=policy,
        )

        result = usecase.execute(
            RefreshStudentHouseScoreCommand(
                observation_version=args.observation_version,
                policy=policy,
            )
        )

        print(f"observation_version={result.observation_version}")
        print(f"policy_version={result.policy_version}")
        print(
            f"observations={result.total_observations} "
            f"processed={result.processed_count} failed={result.failed_count}"
        )
    finally:
        if generator:
            generator.close()
        else:
            session.close()


if __name__ == "__main__":
    main()
