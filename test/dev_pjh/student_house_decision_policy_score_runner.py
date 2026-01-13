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
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCriteria,
)
from modules.student_house_decision_policy.application.usecase.refresh_student_house_score import (
    RefreshStudentHouseScoreService,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)
from infrastructure.db.postgres import SessionLocal
from infrastructure.db.session_helper import open_session
from modules.house_platform.infrastructure.repository.house_platform_repository import (
    HousePlatformRepository,
)
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
from modules.observations.application.usecase.generate_full_observation_usecase import (
    GenerateFullObservationUseCase,
)
from modules.observations.application.usecase.generate_distance_observation_usecase import (
    GenerateDistanceObservationUseCase,
)
from modules.observations.application.usecase.generate_price_observation_usecase import (
    GeneratePriceObservationUseCase,
)
from modules.observations.application.usecase.generate_student_recommendation_feature_observation_usecase import (
    GenerateStudentRecommendationFeatureObservationUseCase,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observation-version",
        type=str,
        default="v1",
        help="관측 버전",
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
        house_platform_detail_repo = HousePlatformRepository()
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

        candidates = house_platform_repo.fetch_candidates(
            FilterCandidateCriteria(
                max_deposit_limit=None,
                max_rent_limit=None,
                budget_margin_ratio=0.0,
            ),
            limit=None,
        )
        price_map: dict[int, int] = {}
        for candidate in candidates:
            monthly_total = 0
            if candidate.monthly_rent is not None:
                monthly_total += candidate.monthly_rent
            if candidate.manage_cost is not None:
                monthly_total += candidate.manage_cost
            price_value = (
                candidate.deposit
                if candidate.deposit is not None
                else monthly_total
            )
            # TODO: price_map 기준(보증금/월세/관리비 가중) 확정 시 수정한다.
            price_map[candidate.house_platform_id] = int(price_value)

        distance_uc = GenerateDistanceObservationUseCase(
            distance_repo=distance_repo,
            house_repo=house_platform_detail_repo,
            university_repo=university_repo,
        )
        price_uc = GeneratePriceObservationUseCase(
            price_repo=price_repo,
            house_prices=price_map,
        )
        feature_uc = GenerateStudentRecommendationFeatureObservationUseCase(
            observation_repo=feature_repo,
            distance_usecase=None,
            house_repo=house_platform_detail_repo,
        )
        full_uc = GenerateFullObservationUseCase(
            student_feature_uc=feature_uc,
            price_uc=price_uc,
            distance_uc=distance_uc,
        )
        
        obs_processed = 0
        obs_failed = 0
        total_candidates = len(candidates)
        print(f"Generating observations for {total_candidates} candidates...")
        
        for i, candidate in enumerate(candidates, 1):
            try:
                full_uc.execute(candidate.house_platform_id)
                obs_processed += 1
            except Exception as e:
                obs_failed += 1
                # print(f"[Warning] Failed to generate observation for house {candidate.house_platform_id}: {e}")
            
            if i % 10 == 0:
                print(f"Progress: {i}/{total_candidates} ({(i/total_candidates)*100:.1f}%) - Processed: {obs_processed}, Failed: {obs_failed}", end='\r')
        
        print() # Newline after loop
        print(f"Observation generation finished: processed={obs_processed}, failed={obs_failed}")

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
