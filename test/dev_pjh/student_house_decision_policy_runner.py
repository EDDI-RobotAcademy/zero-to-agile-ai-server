"""student_house_decision_policy finder_request 기반 필터링 러너."""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from infrastructure.db.postgres import get_db_session
from modules.finder_request.adapter.output.repository.finder_request_repository import (
    FinderRequestRepository,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCommand,
)
from modules.student_house_decision_policy.application.usecase.filter_candidate import (
    FilterCandidateService,
)
from modules.student_house_decision_policy.domain.value_object.budget_filter_policy import (
    BudgetFilterPolicy,
)
from modules.student_house_decision_policy.infrastructure.repository.house_platform_candidate_repository import (
    HousePlatformCandidateRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finder-request-id", type=int, required=True)
    parser.add_argument(
        "--budget-margin-ratio",
        type=float,
        default=None,
        help="예산 여유율(기본값은 Policy 기본값 사용)",
    )
    parser.add_argument(
        "--display-limit",
        type=int,
        default=10,
        help="출력용 후보 표시 개수",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    db_gen = get_db_session()
    db = next(db_gen)
    try:
        finder_request_repo = FinderRequestRepository(db)
        house_platform_repo = HousePlatformCandidateRepository()
        policy = (
            BudgetFilterPolicy(budget_margin_ratio=args.budget_margin_ratio)
            if args.budget_margin_ratio is not None
            else BudgetFilterPolicy()
        )
        usecase = FilterCandidateService(
            finder_request_repo,
            house_platform_repo,
            policy=policy,
        )

        result = usecase.execute(
            FilterCandidateCommand(finder_request_id=args.finder_request_id)
        )

        print(f"finder_request_id={result.finder_request_id}")
        print(
            "criteria: "
            f"deposit_limit={result.criteria.max_deposit_limit} "
            f"rent_limit={result.criteria.max_rent_limit} "
            f"margin_ratio={result.criteria.budget_margin_ratio}"
        )
        print(
            "filters: "
            f"price_type={result.criteria.price_type} "
            f"preferred_region={result.criteria.preferred_region} "
            f"house_type={result.criteria.house_type}"
        )
        if result.message:
            print(f"message={result.message}")
            return

        candidates = list(result.candidates)
        print(f"candidates: {len(candidates)}")
        for idx, item in enumerate(candidates[: args.display_limit], start=1):
            print(
                f"{idx}. house_platform_id={item.house_platform_id} "
                f"deposit={item.deposit} "
                f"monthly_rent={item.monthly_rent} "
                f"manage_cost={item.manage_cost}"
            )
    finally:
        db_gen.close()


if __name__ == "__main__":
    main()
