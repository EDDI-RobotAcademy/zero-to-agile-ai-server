from __future__ import annotations

from typing import List, Optional

from modules.finder_request.application.port.finder_request_repository_port import (
    FinderRequestRepositoryPort,
)
from modules.observations.application.port.distance_observation_repository_port import (
    DistanceObservationRepositoryPort,
)
from modules.observations.application.port.price_observation_repository_port import (
    PriceObservationRepositoryPort,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidateCommand,
    FilterCandidateCriteria,
    FilterCandidateResult,
)
from modules.student_house_decision_policy.application.port_in.filter_candidate_port import (
    FilterCandidatePort,
)
from modules.student_house_decision_policy.application.port_out.house_platform_candidate_port import (
    HousePlatformCandidateReadPort,
)
from modules.student_house_decision_policy.domain.value_object.budget_filter_policy import (
    BudgetFilterPolicy,
)
from modules.university.application.port.university_repository_port import (
    UniversityRepositoryPort,
)


class FilterCandidateService(FilterCandidatePort):
    """finder_request 조건으로 후보 매물을 선별한다.

    여유율 변경은 BudgetFilterPolicy 주입으로 조정한다.
    """

    def __init__(
        self,
        finder_request_repo: FinderRequestRepositoryPort,
        house_platform_repo: HousePlatformCandidateReadPort,
        price_observation_repo: PriceObservationRepositoryPort,
        distance_observation_repo: DistanceObservationRepositoryPort,
        university_repo: UniversityRepositoryPort,
        policy: BudgetFilterPolicy | None = None,
    ):
        self.finder_request_repo = finder_request_repo
        self.house_platform_repo = house_platform_repo
        self.price_observation_repo = price_observation_repo
        self.distance_observation_repo = distance_observation_repo
        self.university_repo = university_repo
        self.policy = policy or BudgetFilterPolicy()

    def execute(self, command: FilterCandidateCommand) -> FilterCandidateResult:
        """finder_request 기준으로 후보를 조회한다."""
        request = self.finder_request_repo.find_by_id(
            command.finder_request_id
        )
        if not request:
            criteria = FilterCandidateCriteria(
                max_deposit_limit=None,
                max_rent_limit=None,
                budget_margin_ratio=self.policy.budget_margin_ratio,
            )
            return FilterCandidateResult(
                finder_request_id=command.finder_request_id,
                criteria=criteria,
                candidates=[],
                message="finder_request가 존재하지 않습니다.",
            )

        max_deposit_limit = self.policy.clamp_budget(request.max_deposit)
        max_rent_limit = self.policy.clamp_budget(request.max_rent)
        criteria = FilterCandidateCriteria(
            max_deposit_limit=max_deposit_limit,
            max_rent_limit=max_rent_limit,
            budget_margin_ratio=self.policy.budget_margin_ratio,
            price_type=request.price_type,
            preferred_region=request.preferred_region,
            house_type=request.house_type,
            additional_condition=request.additional_condition,
            university_name=request.university_name,
            is_near=request.is_near,
        )

        if max_deposit_limit is None and max_rent_limit is None:
            return FilterCandidateResult(
                finder_request_id=command.finder_request_id,
                criteria=criteria,
                candidates=[],
                message="예산 조건이 없어 후보를 선별할 수 없습니다.",
            )

        candidates = self._fetch_candidates(criteria)
        candidates = self._filter_by_price_observations(criteria, candidates)
        candidates = self._filter_by_distance_observation(criteria, candidates)
        
        # TODO: 리스크 허용 조건이 준비되면 후보를 추가 필터링한다.
        # TODO: additional_condition 파싱 규칙이 확정되면 필터 조건에 반영한다.

        return FilterCandidateResult(
            finder_request_id=command.finder_request_id,
            criteria=criteria,
            candidates=candidates,
            message=None,
        )

    def _fetch_candidates(
        self,
        criteria: FilterCandidateCriteria,
    ) -> list:
        """finder_request 기본 조건으로 후보를 조회한다."""
        if criteria.max_deposit_limit is None and criteria.max_rent_limit is None:
            return []
        return list(self.house_platform_repo.fetch_candidates(criteria))

    def _filter_by_price_observations(
        self,
        criteria: FilterCandidateCriteria,
        candidates: list,
    ) -> list:
        """관측된 가격 지표(입주비/월비용)로 후보를 필터링한다."""
        filtered = []
        for candidate in candidates:
            observation = self.price_observation_repo.get_by_house_platform_id(
                candidate.house_platform_id
            )
            
            if not observation:
                # 관측값 미존재 시 제외 (정책상 관측값 필수인 경우)
                continue

            if (
                criteria.max_deposit_limit is not None
                and observation.예상_입주비용 > criteria.max_deposit_limit
            ):
                continue
            if (
                criteria.max_rent_limit is not None
                and observation.월_비용_추정 > criteria.max_rent_limit
            ):
                continue
            
            filtered.append(candidate)
        return filtered

    def _filter_by_distance_observation(
        self,
        criteria: FilterCandidateCriteria,
        candidates: list,
    ) -> list:
        """거리 관측치를 사용하여 통학 거리 조건을 필터링한다."""
        if not criteria.university_name or not criteria.is_near:
            # 거리 조건이 없거나 '가까운' 매물을 찾지 않는 경우 필터링 생략
            return candidates

        target_uni_id = self._resolve_university_id(criteria.university_name)
        if not target_uni_id:
            # 해당 대학을 찾을 수 없으면 필터링 불가 (모두 반환하거나 모두 제외, 여기선 원본 반환)
            return candidates

        filtered = []
        for candidate in candidates:
            distances = self.distance_observation_repo.get_bulk_by_house_platform_id(
                candidate.house_platform_id
            )
            
            matched_distance = next(
                (d for d in distances if d.university_id == target_uni_id), 
                None
            )
            
            if not matched_distance:
                # 해당 대학에 대한 거리 정보가 없으면 제외
                continue

            # 통학 거리 30분 이내 (임시 기준) 필터링
            if matched_distance.학교까지_분 <= 30.0:
                filtered.append(candidate)
        
        return filtered

    def _resolve_university_id(self, name: str) -> Optional[int]:
        # TODO: 성능 개선을 위해 캐싱 고려 가능
        locations = self.university_repo.get_university_locations()
        for loc in locations:
            if loc.university_name == name:
                return loc.university_location_id
        return None