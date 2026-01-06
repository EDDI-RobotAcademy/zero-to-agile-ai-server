from __future__ import annotations

from modules.finder_request.application.port.finder_request_repository_port import (
    FinderRequestRepositoryPort,
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


class FilterCandidateService(FilterCandidatePort):
    """finder_request 조건으로 후보 매물을 선별한다.

    여유율 변경은 BudgetFilterPolicy 주입으로 조정한다.
    """

    def __init__(
        self,
        finder_request_repo: FinderRequestRepositoryPort,
        house_platform_repo: HousePlatformCandidateReadPort,
        policy: BudgetFilterPolicy | None = None,
    ):
        self.finder_request_repo = finder_request_repo
        self.house_platform_repo = house_platform_repo
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
        )
        # TODO: finder_request에 필수 옵션/이동 제한/리스크 허용 컬럼이 준비되면 criteria로 확장한다.

        if max_deposit_limit is None and max_rent_limit is None:
            return FilterCandidateResult(
                finder_request_id=command.finder_request_id,
                criteria=criteria,
                candidates=[],
                message="예산 조건이 없어 후보를 선별할 수 없습니다.",
            )

        candidates = self._filter_by_budget(criteria)
        # TODO: 필수 옵션 조건이 준비되면 후보를 추가 필터링한다.
        # TODO: 이동 제한(거리) 조건이 준비되면 후보를 추가 필터링한다.
        # TODO: 리스크 허용 조건이 준비되면 후보를 추가 필터링한다.

        # TODO: additional_condition 파싱 규칙이 확정되면 필터 조건에 반영한다.
        return FilterCandidateResult(
            finder_request_id=command.finder_request_id,
            criteria=criteria,
            candidates=candidates,
            message=None,
        )

    def _filter_by_budget(
        self,
        criteria: FilterCandidateCriteria,
    ) -> list:
        """예산 조건으로 후보를 선별한다."""
        if criteria.max_deposit_limit is None and criteria.max_rent_limit is None:
            return []
        # 예산 필터 기준: 보증금/월세 상한으로 필터링하며, 정렬/제한 없이 반환한다.
        # 정책 수정은 BudgetFilterPolicy를 교체해서 적용한다.
        return list(self.house_platform_repo.fetch_candidates(criteria))
