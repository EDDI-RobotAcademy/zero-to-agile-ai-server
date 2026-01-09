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
from modules.student_house_decision_policy.infrastructure.repository.observation_score_repository import (
    ObservationScoreRepository,
)
from modules.student_house_decision_policy.infrastructure.repository.student_house_score_repository import (
    StudentHouseScoreRepository,
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
    observation_repo = ObservationScoreRepository()
    student_house_repo = StudentHouseScoreRepository()
    usecase = RefreshStudentHouseScoreService(
        observation_repo=observation_repo,
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
    print(f"top_k={len(result.top_candidates)}")
    for idx, item in enumerate(result.top_candidates, start=1):
        print(
            f"{idx}. house_platform_id={item.house_platform_id} "
            f"score={item.base_total_score} "
            f"price={item.price_score} "
            f"option={item.option_score} "
            f"risk={item.risk_score} "
            f"distance={item.distance_score}"
        )


if __name__ == "__main__":
    main()
