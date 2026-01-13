"""student_house_decision_policy mock 필터링 테스트."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from modules.finder_request.domain.finder_request import FinderRequest
from modules.observations.application.port.distance_observation_repository_port import (
    DistanceObservationRepositoryPort,
)
from modules.observations.application.port.price_observation_repository_port import (
    PriceObservationRepositoryPort,
)
from modules.observations.domain.model.distance_feature_observation import (
    DistanceFeatureObservation,
)
from modules.observations.domain.model.price_feature_observation import (
    PriceFeatureObservation,
)
from modules.observations.domain.model.student_recommendation_feature_observation import (
    StudentRecommendationFeatureObservation,
)
from modules.observations.domain.value_objects.convenience_observation_features import (
    ConvenienceObservationFeatures,
)
from modules.observations.domain.value_objects.observation_metadata import (
    ObservationMetadata,
)
from modules.observations.domain.value_objects.observation_notes import (
    ObservationNotes,
)
from modules.observations.domain.value_objects.risk_observation_features import (
    RiskObservationFeatures,
)
from modules.student_house_decision_policy.application.dto.candidate_filter_dto import (
    FilterCandidate,
    FilterCandidateCommand,
    FilterCandidateCriteria,
    ObservationPriceFeatures,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
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
from modules.university.application.dto.university_location_dto import (
    UniversityLocationDTO,
)
from modules.university.application.port.university_repository_port import (
    UniversityRepositoryPort,
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


class _FakePriceObservationRepository(PriceObservationRepositoryPort):
    """가격 관측 데이터 mock 저장소."""

    def __init__(self, data: Dict[int, PriceFeatureObservation]):
        self._data = data

    def save_bulk(self, observations: List[PriceFeatureObservation]) -> None:
        pass

    def save(
        self, observation: PriceFeatureObservation
    ) -> PriceFeatureObservation:
        return observation

    def get_by_house_platform_id(
        self, house_platform_id: int
    ) -> Optional[PriceFeatureObservation]:
        return self._data.get(house_platform_id)


class _FakeDistanceObservationRepository(DistanceObservationRepositoryPort):
    """거리 관측 데이터 mock 저장소."""

    def __init__(self, data: Dict[int, List[DistanceFeatureObservation]]):
        self._data = data

    def save_bulk(self, distances: List[DistanceFeatureObservation]):
        pass

    def get_bulk_by_house_platform_id(
        self, house_platform_id: int
    ) -> List[DistanceFeatureObservation]:
        return self._data.get(house_platform_id, [])


class _FakeUniversityRepository(UniversityRepositoryPort):
    """대학 정보 mock 저장소."""

    def get_all_university_names(self) -> List[str]:
        return ["테스트대학교"]

    def get_university_locations(self) -> List[UniversityLocationDTO]:
        return [
            UniversityLocationDTO(
                university_location_id=999,
                university_name="테스트대학교",
                campus="본캠",
                lat=37.0,
                lng=127.0,
            )
        ]

    def get_unique_university_locations(self) -> List[int]:
        return [999]


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
        university_name="테스트대학교",
        is_near=True,
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

    # Price Observation Mock
    price_obs_1 = PriceFeatureObservation(
        id=1,
        house_platform_id=1,
        recommendation_observation_id=1,
        가격_백분위=0.3,
        가격_z점수=-0.2,
        예상_입주비용=950,
        월_비용_추정=55,
        가격_부담_비선형=0.2,
    )
    price_obs_2 = PriceFeatureObservation(
        id=2,
        house_platform_id=2,
        recommendation_observation_id=1,
        가격_백분위=0.7,
        가격_z점수=0.5,
        예상_입주비용=950,
        월_비용_추정=90,
        가격_부담_비선형=0.8,
    )
    price_observations = {
        1: price_obs_1,
        2: price_obs_2,
    }

    # Distance Observation Mock
    dist_obs_1 = DistanceFeatureObservation(
        id=1,
        house_platform_id=1,
        recommendation_observation_id=1,
        university_id=999,  # "테스트대학교" ID
        학교까지_분=15.0,  # 30분 이내 -> 통과
        거리_백분위=0.1,
        거리_버킷="near",
        거리_비선형_점수=0.9,
    )
    dist_obs_2 = DistanceFeatureObservation(
        id=2,
        house_platform_id=2,
        recommendation_observation_id=1,
        university_id=999,
        학교까지_분=40.0,  # 30분 초과 -> 탈락 (가격 조건도 탈락이지만)
        거리_백분위=0.8,
        거리_버킷="far",
        거리_비선형_점수=0.1,
    )
    distance_observations = {
        1: [dist_obs_1],
        2: [dist_obs_2],
    }

    service = FilterCandidateService(
        finder_request_repo=_FakeFinderRequestRepository(request),
        house_platform_repo=_FakeCandidateRepository(candidates),
        price_observation_repo=_FakePriceObservationRepository(
            price_observations
        ),
        distance_observation_repo=_FakeDistanceObservationRepository(
            distance_observations
        ),
        university_repo=_FakeUniversityRepository(),
        policy=BudgetFilterPolicy(),
    )

    result = service.execute(FilterCandidateCommand(finder_request_id=23))

    assert len(result.candidates) == 1
    assert result.candidates[0].house_platform_id == 1


class _FakeFeatureObservationRepository:
    """feature 관측 mock 저장소."""

    def __init__(
        self, rows: Dict[int, StudentRecommendationFeatureObservation]
    ):
        self._rows = rows

    def find_latest_by_house_id(
        self, house_id: int
    ) -> StudentRecommendationFeatureObservation | None:
        return self._rows.get(house_id)


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
    candidates = [
        _CandidateRow(
            house_platform_id=1,
            snapshot_id="snap-1",
            deposit=100,
            monthly_rent=50,
            manage_cost=5,
            sales_type="월세",
            address="서울시",
        ),
        _CandidateRow(
            house_platform_id=2,
            snapshot_id="snap-2",
            deposit=200,
            monthly_rent=100,
            manage_cost=10,
            sales_type="월세",
            address="서울시",
        ),
    ]
    feature_observations = {
        1: StudentRecommendationFeatureObservation(
            id=1,
            house_platform_id=1,
            snapshot_id="snap-1",
            위험_관측치=RiskObservationFeatures(
                위험_사건_개수=0,
                위험_사건_유형=[],
                위험_확률_추정=0.1,
                위험_심각도_점수=0.1,
                위험_비선형_패널티=0.1,
            ),
            편의_관측치=ConvenienceObservationFeatures(
                필수_옵션_커버리지=1.0,
                편의_점수=0.9,
            ),
            관측_메모=ObservationNotes.empty(),
            메타데이터=ObservationMetadata(
                관측치_버전=observation_version,
                원본_데이터_버전="v1",
            ),
        ),
        2: StudentRecommendationFeatureObservation(
            id=2,
            house_platform_id=2,
            snapshot_id="snap-2",
            위험_관측치=RiskObservationFeatures(
                위험_사건_개수=1,
                위험_사건_유형=["RISK"],
                위험_확률_추정=0.9,
                위험_심각도_점수=0.9,
                위험_비선형_패널티=0.9,
            ),
            편의_관측치=ConvenienceObservationFeatures(
                필수_옵션_커버리지=0.2,
                편의_점수=0.2,
            ),
            관측_메모=ObservationNotes.empty(),
            메타데이터=ObservationMetadata(
                관측치_버전=observation_version,
                원본_데이터_버전="v1",
            ),
        ),
    }
    price_observations = {
        1: PriceFeatureObservation(
            id=1,
            house_platform_id=1,
            recommendation_observation_id=1,
            가격_백분위=0.1,
            가격_z점수=-1.0,
            예상_입주비용=1000,
            월_비용_추정=60,
            가격_부담_비선형=0.1,
        ),
        2: PriceFeatureObservation(
            id=2,
            house_platform_id=2,
            recommendation_observation_id=2,
            가격_백분위=0.9,
            가격_z점수=2.0,
            예상_입주비용=3000,
            월_비용_추정=120,
            가격_부담_비선형=0.9,
        ),
    }
    distance_observations = {
        1: [
            DistanceFeatureObservation(
                id=1,
                house_platform_id=1,
                recommendation_observation_id=1,
                university_id=999,
                학교까지_분=5.0,
                거리_백분위=0.1,
                거리_버킷="0_10분",
                거리_비선형_점수=0.9,
            )
        ],
        2: [
            DistanceFeatureObservation(
                id=2,
                house_platform_id=2,
                recommendation_observation_id=2,
                university_id=999,
                학교까지_분=70.0,
                거리_백분위=0.9,
                거리_버킷="40분_이상",
                거리_비선형_점수=0.1,
            )
        ],
    }

    score_repo = _FakeStudentHouseScoreRepository()
    service = RefreshStudentHouseScoreService(
        house_platform_repo=_FakeCandidateRepository(candidates),
        feature_observation_repo=_FakeFeatureObservationRepository(
            feature_observations
        ),
        price_observation_repo=_FakePriceObservationRepository(
            price_observations
        ),
        distance_observation_repo=_FakeDistanceObservationRepository(
            distance_observations
        ),
        university_repo=_FakeUniversityRepository(),
        student_house_repo=score_repo,
        policy=policy,
    )

    result = service.execute(
        RefreshStudentHouseScoreCommand(
            observation_version=observation_version, policy=policy
        )
    )

    assert result.processed_count == 2
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
