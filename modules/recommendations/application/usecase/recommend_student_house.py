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
from modules.student_house_decision_policy.application.port_out.student_house_score_port import (
    StudentHouseScorePort,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)


class RecommendStudentHouseService(RecommendStudentHousePort):
    """학생 매물 추천 결과를 종합한다."""

    def __init__(
        self,
        finder_request_repo: FinderRequestRepositoryPort,
        house_platform_repo: HousePlatformRepositoryPort,
        observation_repo,
        score_repo: StudentHouseScorePort,
        policy: DecisionPolicyConfig | None = None,
    ):
        self.finder_request_repo = finder_request_repo
        self.house_platform_repo = house_platform_repo
        self.observation_repo = observation_repo
        self.score_repo = score_repo
        self.policy = policy or DecisionPolicyConfig()

    def execute(
        self, command: RecommendStudentHouseCommand
    ) -> RecommendStudentHouseResult | None:
        """추천 결과를 생성한다."""
        request = self.finder_request_repo.find_by_id(
            command.finder_request_id
        )
        if not request:
            return None
        candidates = command.candidate_house_platform_ids

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
                policy,
                decision_status="RECOMMENDED",
            ),
            rejected_top_k=self._build_ranked_items(
                rejected_top,
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
            observation = self._fetch_observation(candidate_id)
            if not observation:
                missing_observations.append(candidate_id)
                continue
            snapshot_id = raw.get("snapshot_id")
            if snapshot_id and observation.snapshot_id != snapshot_id:
                snapshot_mismatches.append(candidate_id)

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
        policy: DecisionPolicyConfig,
        decision_status: str,
    ) -> list[dict[str, Any]]:
        results = []
        for index, (house_platform_id, score, _) in enumerate(
            ranked_items, start=1
        ):
            raw = self._build_raw(house_platform_id)
            observation = self._fetch_observation(
                house_platform_id
            )
            observation_summary = self._build_observation_summary(
                observation, raw.get("snapshot_id")
            )
            score_breakdown = self._build_score_breakdown(score, policy)
            version_mismatch = self._has_version_mismatch(
                score, observation
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
                    "reasons_top3": [],
                    "warnings": self._build_warnings(version_mismatch),
                }
                # TODO: ai_explaination 모듈 연동 시 실제 설명을 채운다.
            else:
                item["reject_reasons"] = [
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
                item["explanation"] = {
                    "reasons_top3": [],
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

    def _fetch_observation(self, house_platform_id: int):
        """관측 저장소의 메서드 차이를 내부에서 흡수한다."""
        if not hasattr(self.observation_repo, "find_latest_by_house_id"):
            raise AttributeError("관측 저장소가 없습니다.")
        return self.observation_repo.find_latest_by_house_id(
            house_platform_id
        )

    @staticmethod
    def _build_observation_summary(
        observation,
        snapshot_id: str | None,
    ) -> dict[str, Any] | None:
        if not observation:
            return None
        if snapshot_id and observation.snapshot_id != snapshot_id:
            # TODO: snapshot_id 불일치 처리 정책을 확정한다.
            return None
        return {
            "snapshot_id": observation.snapshot_id,
            "observation_version": observation.메타데이터.관측치_버전,
            "source_data_version": observation.메타데이터.원본_데이터_버전,
            "calculated_at": observation.calculated_at.isoformat()
            if observation.calculated_at
            else None,
            "price": {
                "monthly_cost_est": observation.가격_관측치.월_비용_추정,
                "price_percentile": observation.가격_관측치.가격_백분위,
                "price_zscore": observation.가격_관측치.가격_z점수,
                "price_burden_nonlinear": observation.가격_관측치.가격_부담_비선형,
                "estimated_move_in_cost": observation.가격_관측치.예상_입주비용,
            },
            "commute": {
                "distance_to_school_min": observation.거리_관측치.학교까지_분,
                "distance_bucket": observation.거리_관측치.거리_버킷,
                "distance_percentile": observation.거리_관측치.거리_백분위,
                "distance_nonlinear_score": observation.거리_관측치.거리_비선형_점수,
                # TODO: 거리 상세 정보는 observation 모듈에서 제공되면 추가한다.
                "distance_details_top3": [],
            },
            "risk": {
                "risk_event_count": observation.위험_관측치.위험_사건_개수,
                "risk_event_types": observation.위험_관측치.위험_사건_유형,
                "risk_probability_est": observation.위험_관측치.위험_확률_추정,
                "risk_severity_score": observation.위험_관측치.위험_심각도_점수,
                "risk_nonlinear_penalty": observation.위험_관측치.위험_비선형_패널티,
            },
            "options": {
                "essential_option_coverage": observation.편의_관측치.필수_옵션_커버리지,
                "convenience_score": observation.편의_관측치.편의_점수,
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
