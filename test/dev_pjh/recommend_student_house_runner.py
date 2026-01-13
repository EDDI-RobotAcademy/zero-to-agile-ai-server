"""recommendations RecommendStudentHouseUseCase 실행 러너."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseCommand,
)
from modules.recommendations.application.usecase.recommend_student_house import (
    RecommendStudentHouseUseCase,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finder-request-id", type=int, required=True)
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="결과 JSON을 보기 좋게 출력한다.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    usecase = RecommendStudentHouseUseCase()
    result = usecase.execute(
        RecommendStudentHouseCommand(finder_request_id=args.finder_request_id)
    )

    if args.pretty:
        print(
            json.dumps(
                asdict(result), ensure_ascii=False, indent=2
            )
        )
        return

    print(f"finder_request_id={result.finder_request_id}")
    print(f"generated_at={result.generated_at}")
    print(
        "summary: "
        f"total={result.summary.get('total_candidates')} "
        f"recommended={result.summary.get('recommended_count')} "
        f"rejected={result.summary.get('rejected_count')}"
    )
    if result.recommended_top_k:
        top = result.recommended_top_k[0]
        print(
            "top_recommended: "
            f"rank={top.get('rank')} "
            f"house_platform_id={top.get('house_platform_id')}"
        )
        print(
            "recommended_ai_explanation="
            f"{top.get('ai_explanation')}"
        )
    if result.rejected_top_k:
        top = result.rejected_top_k[0]
        print(
            "top_rejected: "
            f"rank={top.get('rank')} "
            f"house_platform_id={top.get('house_platform_id')}"
        )
        print(
            "rejected_ai_explanation="
            f"{top.get('ai_explanation')}"
        )


if __name__ == "__main__":
    main()
