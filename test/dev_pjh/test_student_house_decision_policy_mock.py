"""student_house_decision_policy mock 필터링 테스트."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from modules.finder_request.domain.finder_request import FinderRequest
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidate,
    FilterCandidateCommand,
    FilterCandidateCriteria,
    ObservationPriceFeatures,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    ObservationScoreSource,
    RefreshStudentHouseScoreCommand,
    StudentHouseScoreQuery,
    StudentHouseScoreSummary,
)
from modules.student_house_decision_policy.application.usecase.filter_candidate import (
    FilterCandidateService,
)
from modules.student_house_decision_policy.application.usecase.refresh_student_house_score import (
    RefreshStudentHouseScoreService,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)
from modules.student_house_decision_policy.domain.value_object.budget_filter_policy import (
    BudgetFilterPolicy,
)


@dataclass
class _CandidateRow:
    """house_platform 후보 데이터 mock."""

    house_platform_id: int
    snapshot_id: str
    deposit: int
    monthly_rent: int | None
    manage_cost: int | None
    sales_type: str
    address: str


class _FakeFinderRequestRepository:
    """finder_request mock 저장소."""

    def __init__(self, request: FinderRequest):
        self._request = request

    def find_by_id(self, finder_request_id: int) -> FinderRequest | None:
        return (
            self._request
            if self._request.finder_request_id == finder_request_id
            else None
        )


class _FakeCandidateRepository:
    """house_platform 후보 mock 저장소."""

    def __init__(self, rows: List[_CandidateRow]):
        self._rows = rows

    def fetch_candidates(
        self, criteria: FilterCandidateCriteria, limit: int | None = None
    ) -> List[FilterCandidate]:
        rows = self._rows
        rows = self._apply_price_type(rows, criteria.price_type)
        rows = self._apply_region(rows, criteria.preferred_region)
        if limit is not None:
            rows = rows[:limit]
        return [
            FilterCandidate(
                house_platform_id=row.house_platform_id,
                snapshot_id=row.snapshot_id,
                deposit=row.deposit,
                monthly_rent=row.monthly_rent,
                manage_cost=row.manage_cost,
            )
            for row in rows
        ]

    @staticmethod
    def _apply_price_type(
        rows: List[_CandidateRow], price_type: str | None
    ) -> List[_CandidateRow]:
        if not price_type:
            return rows
        key = price_type.upper()
        if key == "JEONSE":
            return [row for row in rows if "전세" in row.sales_type]
        if key == "MONTHLY":
            return [row for row in rows if "월세" in row.sales_type]
        if key == "MIXED":
            return [
                row
                for row in rows
                if ("전세" in row.sales_type or "월세" in row.sales_type)
            ]
        return rows

    @staticmethod
    def _apply_region(
        rows: List[_CandidateRow], preferred_region: str | None
    ) -> List[_CandidateRow]:
        token = _extract_region_token(preferred_region or "")
        if not token:
            return rows
        return [row for row in rows if token in row.address]


class _FakeObservationRepository:
    """관측 데이터 mock 저장소."""

    def __init__(
        self,
        rows: Dict[Tuple[int, str], ObservationPriceFeatures],
    ):
        self._rows = rows

    def fetch_price_features(
        self, house_platform_id: int, snapshot_id: str
    ) -> ObservationPriceFeatures | None:
        return self._rows.get((house_platform_id, snapshot_id))


def _extract_region_token(preferred_region: str) -> str | None:
    """선호 지역 문자열에서 첫 번째 구 정보를 추출한다."""
    if not preferred_region:
        return None
    tokens = [
        token.strip()
        for token in preferred_region.replace(",", " ").split()
        if token.strip()
    ]
    if not tokens:
        return None
    for token in tokens:
        if token.endswith("구"):
            return token
    return tokens[0]


def test_filter_candidate_with_mock_observation() -> None:
    """관측 지표 기준으로 후보가 선별되는지 확인한다."""
    request = FinderRequest(
        abang_user_id=1,
        status="Y",
        finder_request_id=23,
        preferred_region="마포구 노고산동",
        price_type="MONTHLY",
        max_deposit=1000,
        max_rent=60,
        house_type=None,
        additional_condition=None,
    )

    candidates = [
        _CandidateRow(
            house_platform_id=1,
            snapshot_id="snap-1",
            deposit=900,
            monthly_rent=50,
            manage_cost=5,
            sales_type="월세",
            address="서울 마포구 노고산동 1-1",
        ),
        _CandidateRow(
            house_platform_id=2,
            snapshot_id="snap-2",
            deposit=900,
            monthly_rent=80,
            manage_cost=5,
            sales_type="월세",
            address="서울 마포구 노고산동 2-2",
        ),
        _CandidateRow(
            house_platform_id=3,
            snapshot_id="snap-3",
            deposit=900,
            monthly_rent=None,
            manage_cost=None,
            sales_type="전세",
            address="서울 마포구 노고산동 3-3",
        ),
    ]

    observations = {
        (1, "snap-1"): ObservationPriceFeatures(
            house_platform_id=1,
            snapshot_id="snap-1",
            estimated_move_in_cost=950,
            monthly_cost_est=55,
            price_percentile=0.3,
            price_zscore=-0.2,
            price_burden_nonlinear=0.2,
        ),
        (2, "snap-2"): ObservationPriceFeatures(
            house_platform_id=2,
            snapshot_id="snap-2",
            estimated_move_in_cost=950,
            monthly_cost_est=90,
            price_percentile=0.7,
            price_zscore=0.5,
            price_burden_nonlinear=0.8,
        ),
    }

    service = FilterCandidateService(
        _FakeFinderRequestRepository(request),
        _FakeCandidateRepository(candidates),
        _FakeObservationRepository(observations),
        policy=BudgetFilterPolicy(),
    )

    result = service.execute(FilterCandidateCommand(finder_request_id=23))

    assert len(result.candidates) == 1
    assert result.candidates[0].house_platform_id == 1


class _FakeObservationScoreRepository:
    """관측 테이블 mock 저장소."""

    def __init__(self, rows: List[ObservationScoreSource]):
        self._rows = rows

    def fetch_by_version(
        self, observation_version: str | None
    ) -> List[ObservationScoreSource]:
        if not observation_version:
            return list(self._rows)
        return [
            row
            for row in self._rows
            if row.observation_version == observation_version
        ]


class _FakeStudentHouseScoreRepository:
    """student_house 점수 mock 저장소."""

    def __init__(self):
        self._items: Dict[int, StudentHouseScoreSummary] = {}

    def upsert_score(self, score):
        self._items[score.house_platform_id] = StudentHouseScoreSummary(
            house_platform_id=score.house_platform_id,
            base_total_score=score.base_total_score,
            price_score=score.price_score,
            option_score=score.option_score,
            risk_score=score.risk_score,
            distance_score=score.distance_score,
            observation_version=score.observation_version,
            policy_version=score.policy_version,
        )
        return score.house_platform_id

    def mark_failed(self, house_platform_id: int, reason: str) -> None:
        self._items.pop(house_platform_id, None)

    def fetch_top_k(self, query: StudentHouseScoreQuery):
        items = [
            item
            for item in self._items.values()
            if item.base_total_score >= query.threshold_base_total
        ]
        if query.observation_version:
            items = [
                item
                for item in items
                if item.observation_version == query.observation_version
            ]
        if query.policy_version:
            items = [
                item
                for item in items
                if item.policy_version == query.policy_version
            ]
        items.sort(key=lambda row: row.base_total_score, reverse=True)
        return items[: query.limit]


def test_refresh_student_house_score_with_mock_observation() -> None:
    """관측 기반 스코어 계산/정렬이 동작하는지 확인한다."""
    policy = DecisionPolicyConfig(
        threshold_base_total=50.0, top_k=1, policy_version="v-test"
    )
    observation_version = "20240901"
    observations = [
        ObservationScoreSource(
            house_platform_id=1,
            snapshot_id="snap-1",
            observation_version=observation_version,
            price_percentile=0.1,
            price_zscore=-1.0,
            price_burden_nonlinear=0.1,
            estimated_move_in_cost=1000,
            monthly_cost_est=60,
            essential_option_coverage=1.0,
            convenience_score=0.9,
            risk_probability_est=0.1,
            risk_severity_score=0.1,
            risk_nonlinear_penalty=0.1,
            distance_to_school_min=5.0,
            distance_percentile=0.1,
            distance_nonlinear_score=0.9,
        ),
        ObservationScoreSource(
            house_platform_id=2,
            snapshot_id="snap-2",
            observation_version=observation_version,
            price_percentile=0.9,
            price_zscore=2.0,
            price_burden_nonlinear=0.9,
            estimated_move_in_cost=3000,
            monthly_cost_est=120,
            essential_option_coverage=0.2,
            convenience_score=0.2,
            risk_probability_est=0.9,
            risk_severity_score=0.9,
            risk_nonlinear_penalty=0.9,
            distance_to_school_min=70.0,
            distance_percentile=0.9,
            distance_nonlinear_score=0.1,
        ),
    ]

    score_repo = _FakeStudentHouseScoreRepository()
    service = RefreshStudentHouseScoreService(
        observation_repo=_FakeObservationScoreRepository(observations),
        student_house_repo=score_repo,
        policy=policy,
    )

    result = service.execute(
        RefreshStudentHouseScoreCommand(
            observation_version=observation_version, policy=policy
        )
    )

    assert result.processed_count == 2
    assert len(result.top_candidates) == 1
    assert result.top_candidates[0].house_platform_id == 1

    for item in score_repo._items.values():
        print(
            "score_result "
            f"house_platform_id={item.house_platform_id} "
            f"base_total_score={item.base_total_score} "
            f"price_score={item.price_score} "
            f"option_score={item.option_score} "
            f"risk_score={item.risk_score} "
            f"distance_score={item.distance_score}"
        )
