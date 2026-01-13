from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from modules.finder_request.application.port.finder_request_repository_port import (
    FinderRequestRepositoryPort,
)
from modules.house_platform.application.port_out.house_platform_repository_port import (
    HousePlatformRepositoryPort,
)
from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseCommand,
    RecommendStudentHouseResult,
)
from modules.recommendations.application.port_in.recommend_student_house_port import (
    RecommendStudentHousePort,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCommand,
)
from modules.student_house_decision_policy.application.port_in.filter_candidate_port import (
    FilterCandidatePort,
)
from modules.student_house_decision_policy.application.port_out.student_house_score_port import (
    StudentHouseScorePort,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)
from modules.observations.application.port.price_observation_repository_port import (
    PriceObservationRepositoryPort,
)
from modules.observations.application.port.distance_observation_repository_port import (
    DistanceObservationRepositoryPort,
)
from modules.observations.domain.value_objects.distance_observation_features import (
    DistanceObservationFeatures,
)
from modules.university.application.port.university_repository_port import (
    UniversityRepositoryPort,
)


class RecommendStudentHouseUseCase(RecommendStudentHousePort):
    """학생 매물 추천 결과를 종합한다."""

    def __init__(
        self,
        finder_request_repo: FinderRequestRepositoryPort,
        house_platform_repo: HousePlatformRepositoryPort,
        observation_repo,
        score_repo: StudentHouseScorePort,
        price_observation_repo: PriceObservationRepositoryPort | None = None,
        distance_observation_repo: DistanceObservationRepositoryPort | None = None,
        university_repo: UniversityRepositoryPort | None = None,
        filter_usecase: FilterCandidatePort | None = None,
        build_context_signal_usecase=None,
        policy: DecisionPolicyConfig | None = None,
    ):
        self.finder_request_repo = finder_request_repo
        self.house_platform_repo = house_platform_repo
        self.observation_repo = observation_repo
        self.score_repo = score_repo
        self.price_observation_repo = price_observation_repo
        self.distance_observation_repo = distance_observation_repo
        self.university_repo = university_repo
        self.filter_usecase = filter_usecase
        self.build_context_signal_usecase = build_context_signal_usecase
        self.policy = policy or DecisionPolicyConfig()

    def execute(self, command: RecommendStudentHouseCommand) -> RecommendStudentHouseResult:
        """추천 결과를 생성한다."""
        request = self.finder_request_repo.find_by_id(command.finder_request_id)
        # finder_request는 상위 흐름에서 존재를 보장한다.

        candidates = command.candidate_house_platform_ids
        if candidates is None:
            if not self.filter_usecase:
                raise ValueError("filter_usecase가 필요합니다.")
            filter_result = self.filter_usecase.execute(
                FilterCandidateCommand(
                    finder_request_id=command.finder_request_id
                )
            )
            candidates = [
                candidate.house_platform_id
                for candidate in filter_result.candidates
            ]

        if self.build_context_signal_usecase and candidates:
            self.build_context_signal_usecase.execute_with_candidates(
                candidates
            )

        policy = self.policy
        score_map = self._fetch_score_map(
            candidates,
            policy,
        )
        ranked = [
            (
                house_platform_id,
                score_map.get(house_platform_id),
                self._resolve_base_score(score_map.get(house_platform_id)),
            )
            for house_platform_id in candidates
        ]

        recommended = [item for item in ranked if item[2] >= policy.threshold_base_total]
        rejected = [item for item in ranked if item[2] < policy.threshold_base_total]

        recommended.sort(key=lambda item: item[2], reverse=True)
        rejected.sort(key=lambda item: item[2], reverse=True)

        recommended_top = recommended[: policy.top_k]
        rejected_top = rejected[: policy.top_k]

        # 정상 응답은 SUCCESS + detail None으로 기록한다.
        # TODO: 실패 수집 로직 활성화 시 FAILED + detail 채움으로 전환한다.
        status = "SUCCESS"
        detail = None
        # TODO: 추천 로직이 안정화되면 실패 상세를 활성화한다.
        # detail = self._collect_failure_detail(
        #     candidates=candidates,
        #     score_map=score_map,
        # )
        # if detail:
        #     status = "FAILED"

        result = RecommendStudentHouseResult(
            finder_request_id=command.finder_request_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            status=status,
            detail=detail,
            query_context=self._build_query_context(request, policy),
            summary=self._build_summary(
                total_candidates=len(candidates),
                recommended_count=len(recommended),
                rejected_count=len(rejected),
                top_k=policy.top_k,
            ),
            recommended_top_k=self._build_ranked_items(
                recommended_top,
                request,
                policy,
                decision_status="RECOMMENDED",
            ),
            rejected_top_k=self._build_ranked_items(
                rejected_top,
                request,
                policy,
                decision_status="REJECTED",
            ),
        )
        return result

    def _fetch_score_map(
        self,
        house_platform_ids: list[int],
        policy: DecisionPolicyConfig,
    ) -> dict[int, Any]:
        if not house_platform_ids:
            return {}
        scores = self.score_repo.fetch_by_house_platform_ids(
            house_platform_ids, policy_version=policy.policy_version
        )
        return {score.house_platform_id: score for score in scores}

    def _collect_failure_detail(
        self,
        candidates: list[int],
        score_map: dict[int, Any],
    ) -> dict[str, Any] | None:
        """실패 케이스 정보를 수집한다."""
        failures: list[dict[str, Any]] = []

        if not candidates:
            failures.append(
                {
                    "code": "NO_CANDIDATES",
                    "message": "후보 매물이 없습니다.",
                }
            )
            return {"failures": failures}

        missing_scores = [
            candidate_id
            for candidate_id in candidates
            if candidate_id not in score_map
        ]
        if missing_scores:
            failures.append(
                {
                    "code": "MISSING_SCORE",
                    "message": "점수 데이터가 없습니다.",
                    "context": {"house_platform_ids": missing_scores},
                }
            )

        missing_observations: list[int] = []
        snapshot_mismatches: list[int] = []
        for candidate_id in candidates:
            raw = self._build_raw(candidate_id)
            feature_observation = self._fetch_feature_observation(
                candidate_id
            )
            price_observation = self._fetch_price_observation(
                candidate_id
            )
            distance_observation = self._select_distance_observation(
                self._fetch_distance_observations(candidate_id),
                None,
            )
            if (
                not feature_observation
                or not price_observation
                or not distance_observation
            ):
                missing_observations.append(candidate_id)
                continue
            snapshot_id = raw.get("snapshot_id")
            # TODO: snapshot_id 불일치 처리 정책을 확정한 뒤 활성화한다.
            # if (
            #     snapshot_id
            #     and feature_observation.snapshot_id != snapshot_id
            # ):
            #     snapshot_mismatches.append(candidate_id)

        if missing_observations:
            failures.append(
                {
                    "code": "MISSING_OBSERVATION",
                    "message": "관측 데이터가 없습니다.",
                    "context": {"house_platform_ids": missing_observations},
                }
            )
        if snapshot_mismatches:
            failures.append(
                {
                    "code": "SNAPSHOT_MISMATCH",
                    "message": "스냅샷 ID가 일치하지 않습니다.",
                    "context": {"house_platform_ids": snapshot_mismatches},
                }
            )

        return {"failures": failures} if failures else None

    @staticmethod
    def _resolve_base_score(score) -> float:
        if score is None:
            return 0.0
        return float(score.base_total_score)

    @staticmethod
    def _build_summary(
        total_candidates: int,
        recommended_count: int,
        rejected_count: int,
        top_k: int,
    ) -> dict[str, Any]:
        return {
            "total_candidates": total_candidates,
            "recommended_count": recommended_count,
            "rejected_count": rejected_count,
            "top_k": top_k,
            "rejection_top_k": top_k,
        }

    def _build_ranked_items(
        self,
        ranked_items: list[tuple[Any, Any, float]],
        request,
        policy: DecisionPolicyConfig,
        decision_status: str,
    ) -> list[dict[str, Any]]:
        results = []
        for index, (house_platform_id, score, _) in enumerate(
            ranked_items, start=1
        ):
            raw = self._build_raw(house_platform_id)
            feature_observation = self._fetch_feature_observation(
                house_platform_id
            )
            price_observation = self._fetch_price_observation(
                house_platform_id
            )
            distance_observations = self._fetch_distance_observations(
                house_platform_id
            )
            distance_observation = self._select_distance_observation(
                distance_observations, request
            )
            observation_summary = self._build_observation_summary(
                feature_observation,
                price_observation,
                distance_observation,
                raw.get("snapshot_id"),
            )
            score_breakdown = self._build_score_breakdown(score, policy)
            version_mismatch = self._has_version_mismatch(
                score, feature_observation
            )
            if version_mismatch:
                # TODO: 관측 버전/점수 버전 불일치 처리 정책을 확정한다.
                score_breakdown = None

            item = {
                "rank": index,
                "decision_status": decision_status,
                "house_platform_id": house_platform_id,
                "raw": raw,
                "observation_summary": observation_summary,
                "score_breakdown": score_breakdown
                if decision_status == "RECOMMENDED"
                else None,
            }

            if decision_status == "RECOMMENDED":
                item["ai_explanation"] = {
                    "recommended_reasons": [],
                    "warnings": self._build_warnings(version_mismatch),
                }
                # TODO: explain_by_feature_observations_usecase 연동 시 실제 설명을 채운다.
            else:
                reject_reasons = [
                    {
                        "code": "SCORE_BELOW_THRESHOLD",
                        "text": "점수 기준 미달로 제외되었습니다.",
                        "evidence": {
                            "base_total_score": score.base_total_score
                            if score
                            else 0.0,
                            "threshold": policy.threshold_base_total,
                        },
                    }
                ]
                item["reject_reasons"] = reject_reasons
                item["ai_explanation"] = {
                    "reject_reasons": reject_reasons,
                    "warnings": self._build_reject_warnings(
                        version_mismatch
                    ),
                }
            results.append(item)
        return results

    def _build_raw(self, house_platform_id: int) -> dict[str, Any]:
        """house_platform 도메인 객체를 dict로 변환한다."""
        house = self.house_platform_repo.find_by_id(house_platform_id)
        if not house:
            return {}
        raw = asdict(house)
        raw.pop("crawled_at", None)
        return raw

    def _fetch_feature_observation(self, house_platform_id: int):
        """risk/option 관측 저장소를 조회한다."""
        if not hasattr(self.observation_repo, "find_latest_by_house_id"):
            raise AttributeError("관측 저장소가 없습니다.")
        return self.observation_repo.find_latest_by_house_id(
            house_platform_id
        )

    def _fetch_price_observation(self, house_platform_id: int):
        """가격 관측 저장소를 조회한다."""
        if not self.price_observation_repo:
            raise AttributeError("가격 관측 저장소가 없습니다.")
        return self.price_observation_repo.get_by_house_platform_id(
            house_platform_id
        )

    def _fetch_distance_observations(self, house_platform_id: int):
        """거리 관측 저장소를 조회한다."""
        if not self.distance_observation_repo:
            raise AttributeError("거리 관측 저장소가 없습니다.")
        return self.distance_observation_repo.get_bulk_by_house_platform_id(
            house_platform_id
        )

    def _select_distance_observation(self, distances: list, request):
        """대학교 기준으로 거리 관측치를 선택한다."""
        if not distances:
            return None

        matched = self._find_distance_by_university(distances, request)
        if matched:
            return DistanceObservationFeatures(
                학교까지_분=matched.학교까지_분,
                거리_백분위=matched.거리_백분위,
                거리_버킷=matched.거리_버킷,
                거리_비선형_점수=matched.거리_비선형_점수,
            )

        return self._average_latest_distance(distances)

    def _find_distance_by_university(self, distances: list, request):
        if not request or not request.university_name:
            return None
        if not self.university_repo:
            return None

        target_ids = self._resolve_university_ids(
            request.university_name
        )
        if not target_ids:
            return None

        matched = [
            distance
            for distance in distances
            if distance.university_id in target_ids
        ]
        if not matched:
            return None
        # 동일 학교가 여러 개면 가장 가까운 거리값을 사용한다.
        return min(matched, key=lambda item: item.학교까지_분)

    def _resolve_university_ids(self, university_name: str) -> list[int]:
        normalized = (university_name or "").strip()
        if not normalized:
            return []
        locations = self.university_repo.get_university_locations()
        return [
            location.university_location_id
            for location in locations
            if (location.university_name or "").strip() == normalized
        ]

    @staticmethod
    def _average_latest_distance(distances: list):
        """최신 관측치의 평균값을 계산한다."""
        latest_time = None
        for distance in distances:
            if not distance.calculated_at:
                continue
            if latest_time is None or distance.calculated_at > latest_time:
                latest_time = distance.calculated_at

        latest_distances = [
            distance
            for distance in distances
            if not latest_time
            or distance.calculated_at == latest_time
        ]
        if not latest_distances:
            return None

        avg_minutes = sum(
            distance.학교까지_분 for distance in latest_distances
        ) / len(latest_distances)
        avg_percentile = sum(
            distance.거리_백분위 for distance in latest_distances
        ) / len(latest_distances)
        avg_score = sum(
            distance.거리_비선형_점수 for distance in latest_distances
        ) / len(latest_distances)

        return DistanceObservationFeatures(
            학교까지_분=avg_minutes,
            거리_백분위=avg_percentile,
            거리_버킷=RecommendStudentHouseUseCase._calc_distance_bucket(
                avg_minutes
            ),
            거리_비선형_점수=avg_score,
        )

    @staticmethod
    def _calc_distance_bucket(minutes: float) -> str:
        if minutes < 10:
            return "0_10분"
        if minutes < 20:
            return "10_20분"
        if minutes < 30:
            return "20_30분"
        if minutes < 40:
            return "30_40분"
        return "40분_이상"

    @staticmethod
    def _build_observation_summary(
        feature_observation,
        price_observation,
        distance_observation,
        snapshot_id: str | None,
    ) -> dict[str, Any] | None:
        if not feature_observation or not price_observation or not distance_observation:
            return None
        # TODO: snapshot_id 불일치 처리 정책을 확정한 뒤 활성화한다.
        # if snapshot_id and feature_observation.snapshot_id != snapshot_id:
        #     return None
        return {
            "snapshot_id": feature_observation.snapshot_id,
            "observation_version": feature_observation.메타데이터.관측치_버전,
            "source_data_version": feature_observation.메타데이터.원본_데이터_버전,
            "calculated_at": feature_observation.calculated_at.isoformat()
            if feature_observation.calculated_at
            else None,
            "price": {
                "monthly_cost_est": price_observation.월_비용_추정,
                "price_percentile": price_observation.가격_백분위,
                "price_zscore": price_observation.가격_z점수,
                "price_burden_nonlinear": price_observation.가격_부담_비선형,
                "estimated_move_in_cost": price_observation.예상_입주비용,
            },
            "commute": {
                "distance_to_school_min": distance_observation.학교까지_분,
                "distance_bucket": distance_observation.거리_버킷,
                "distance_percentile": distance_observation.거리_백분위,
                "distance_nonlinear_score": distance_observation.거리_비선형_점수,
                # TODO: 거리 상세 정보는 observation 모듈에서 제공되면 추가한다.
                "distance_details_top3": [],
            },
            "risk": {
                "risk_event_count": feature_observation.위험_관측치.위험_사건_개수,
                "risk_event_types": feature_observation.위험_관측치.위험_사건_유형,
                "risk_probability_est": feature_observation.위험_관측치.위험_확률_추정,
                "risk_severity_score": feature_observation.위험_관측치.위험_심각도_점수,
                "risk_nonlinear_penalty": feature_observation.위험_관측치.위험_비선형_패널티,
            },
            "options": {
                "essential_option_coverage": feature_observation.편의_관측치.필수_옵션_커버리지,
                "convenience_score": feature_observation.편의_관측치.편의_점수,
            },
        }

    @staticmethod
    def _build_score_breakdown(
        score,
        policy: DecisionPolicyConfig,
    ) -> dict[str, Any] | None:
        if not score:
            # TODO: 점수가 없을 때 계산/대체 정책을 확정한다.
            return None
        return {
            "weights": {
                "price": policy.weight_price,
                "risk": policy.weight_risk,
                "option": policy.weight_option,
                "distance": policy.weight_distance,
            },
            "price_score": score.price_score,
            "option_score": score.option_score,
            "risk_score": score.risk_score,
            "distance_score": score.distance_score,
            "total_score": score.base_total_score,
        }

    @staticmethod
    def _has_version_mismatch(score, observation) -> bool:
        if not score or not observation:
            return False
        return (
            score.observation_version
            != observation.메타데이터.관측치_버전
        )

    @staticmethod
    def _build_warnings(version_mismatch: bool) -> list[str]:
        warnings = ["추천 설명은 추후 생성됩니다."]
        if version_mismatch:
            warnings.append("관측 버전과 점수 버전이 일치하지 않습니다.")
        return warnings

    @staticmethod
    def _build_reject_warnings(version_mismatch: bool) -> list[str]:
        warnings = ["점수 기준 미달로 후보에서 제외되었습니다."]
        if version_mismatch:
            warnings.append("관측 버전과 점수 버전이 일치하지 않습니다.")
        return warnings
    @staticmethod
    def _build_query_context(
        request,
        policy: DecisionPolicyConfig,
    ) -> dict[str, Any]:
        """요청서 기준으로 쿼리 컨텍스트를 구성한다."""
        return {
            "segment_id": "STUDENT_DEFAULT",
            "policy_version": policy.policy_version,
            # TODO: observation 모듈에서 region_scope 정보를 제공하면 반영한다.
            "region_scope": None,
            # TODO: observation 모듈에서 대표 학교 세트를 제공하면 반영한다.
            "rep_school_set": None,
            # TODO: cohort 규칙 확정 시 반영한다.
            "cohort_rule": None,
            "user_constraints": {
                "budget_deposit_max": request.max_deposit,
                "budget_monthly_max": request.max_rent,
                "price_type": request.price_type,
                "preferred_region": request.preferred_region,
                "house_type": request.house_type,
                "additional_condition": request.additional_condition,
                "is_near": request.is_near,
                "aircon_yn": request.aircon_yn,
                "washer_yn": request.washer_yn,
                "fridge_yn": request.fridge_yn,
                "max_building_age": request.max_building_age,
            },
        }
