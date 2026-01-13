from datetime import datetime, timezone
import os
import sys

# 프로젝트 루트를 sys.path에 추가해 모듈 import를 보장한다.
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.house_platform.domain.house_platform import HousePlatform
from modules.finder_request.domain.finder_request import FinderRequest
from modules.observations.domain.value_objects.convenience_observation_features import (
    ConvenienceObservationFeatures,
)
from modules.observations.domain.model.student_recommendation_feature_observation import (
    StudentRecommendationFeatureObservation,
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
from modules.observations.domain.model.price_feature_observation import (
    PriceFeatureObservation,
)
from modules.observations.domain.model.distance_feature_observation import (
    DistanceFeatureObservation,
)
from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseCommand,
)
from modules.recommendations.application.usecase.recommend_student_house import (
    RecommendStudentHouseUseCase,
)
from modules.recommendations.application.usecase.recommend_student_house_mock import (
    RecommendStudentHouseMockService,
)
from modules.recommendations.application.dto.recommendation_dto import (
    RecommendStudentHouseMockCommand,
)
from modules.student_house_decision_policy.application.dto.decision_score_dto import (
    StudentHouseScoreSummary,
)
from modules.student_house_decision_policy.domain.value_object.decision_policy_config import (
    DecisionPolicyConfig,
)

# house_platform ORM 컬럼 목록을 테스트에서 고정한다.
# TODO: house_platform ORM 컬럼 변경 시 목록을 동기화한다.
HOUSE_PLATFORM_COLUMNS = [
    "house_platform_id",
    "title",
    "address",
    "deposit",
    "abang_user_id",
    "created_at",
    "updated_at",
    "registered_at",
    "domain_id",
    "rgst_no",
    "snapshot_id",
    "pnu_cd",
    "is_banned",
    "sales_type",
    "monthly_rent",
    "room_type",
    "residence_type",
    "contract_area",
    "exclusive_area",
    "floor_no",
    "all_floors",
    "lat_lng",
    "manage_cost",
    "can_park",
    "has_elevator",
    "image_urls",
    "gu_nm",
    "dong_nm",
]


class FakeHousePlatformRepository:
    def find_by_id(self, house_platform_id: int):
        return HousePlatform(
            house_platform_id=house_platform_id,
            title=None,
            address=None,
            deposit=None,
            domain_id=None,
            rgst_no=None,
            sales_type=None,
            monthly_rent=None,
            room_type=None,
            contract_area=None,
            exclusive_area=None,
            floor_no=None,
            all_floors=None,
            lat_lng=None,
            manage_cost=None,
            can_park=None,
            has_elevator=None,
            image_urls=None,
            pnu_cd=None,
            is_banned=None,
            residence_type=None,
            gu_nm=None,
            dong_nm=None,
            registered_at=None,
            crawled_at=None,
            snapshot_id=f"snap-{house_platform_id}",
            abang_user_id=-1,
            created_at=None,
            updated_at=None,
        )


class FakeObservationRepository:
    def __init__(self, observations):
        self._observations = observations

    def find_latest_by_house_id(self, house_platform_id: int):
        return self._observations.get(house_platform_id)


class FakeScoreRepository:
    def __init__(self, scores):
        self._scores = scores

    def fetch_by_house_platform_ids(self, house_platform_ids, policy_version=None):
        return [
            score
            for score in self._scores
            if score.house_platform_id in house_platform_ids
            and (
                policy_version is None
                or score.policy_version == policy_version
            )
        ]

class FakePriceObservationRepository:
    def __init__(self, observations):
        self._observations = observations

    def get_by_house_platform_id(self, house_platform_id: int):
        return self._observations.get(house_platform_id)


class FakeDistanceObservationRepository:
    def __init__(self, observations):
        self._observations = observations

    def get_bulk_by_house_platform_id(self, house_platform_id: int):
        return self._observations.get(house_platform_id, [])


def _build_observation(
    house_platform_id: int, snapshot_id: str
) -> StudentRecommendationFeatureObservation:
    return StudentRecommendationFeatureObservation(
        id=1,
        house_platform_id=house_platform_id,
        snapshot_id=snapshot_id,
        위험_관측치=RiskObservationFeatures(
            위험_사건_개수=0,
            위험_사건_유형=["NONE"],
            위험_확률_추정=0.1,
            위험_심각도_점수=0.2,
            위험_비선형_패널티=0.1,
        ),
        편의_관측치=ConvenienceObservationFeatures(
            필수_옵션_커버리지=0.9,
            편의_점수=0.8,
        ),
        관측_메모=ObservationNotes.empty(),
        메타데이터=ObservationMetadata(
            관측치_버전="obs-1",
            원본_데이터_버전="src-1",
        ),
        calculated_at=datetime.now(timezone.utc),
    )


def test_recommend_student_house_mock():
    finder_request = FinderRequest(
        abang_user_id=1,
        status="Y",
        finder_request_id=10,
        preferred_region="마포구",
        price_type="MONTHLY",
        max_deposit=1000,
        max_rent=80,
    )
    candidate_ids = [1, 2]

    observations = {
        1: _build_observation(1, "snap-1"),
        2: _build_observation(2, "snap-2"),
    }
    price_observations = {
        1: PriceFeatureObservation(
            id=1,
            house_platform_id=1,
            recommendation_observation_id=1,
            가격_백분위=0.2,
            가격_z점수=-0.5,
            예상_입주비용=800,
            월_비용_추정=60,
            가격_부담_비선형=0.4,
        ),
        2: PriceFeatureObservation(
            id=2,
            house_platform_id=2,
            recommendation_observation_id=1,
            가격_백분위=0.8,
            가격_z점수=0.6,
            예상_입주비용=1500,
            월_비용_추정=120,
            가격_부담_비선형=0.8,
        ),
    }
    distance_observations = {
        1: [
            DistanceFeatureObservation(
                id=1,
                house_platform_id=1,
                recommendation_observation_id=1,
                university_id=1,
                학교까지_분=15.0,
                거리_백분위=0.2,
                거리_버킷="10_20분",
                거리_비선형_점수=0.8,
                calculated_at=datetime.now(timezone.utc),
            )
        ],
        2: [
            DistanceFeatureObservation(
                id=2,
                house_platform_id=2,
                recommendation_observation_id=1,
                university_id=1,
                학교까지_분=35.0,
                거리_백분위=0.7,
                거리_버킷="30_40분",
                거리_비선형_점수=0.4,
                calculated_at=datetime.now(timezone.utc),
            )
        ],
    }

    scores = [
        StudentHouseScoreSummary(
            house_platform_id=1,
            base_total_score=80.0,
            price_score=78.0,
            option_score=85.0,
            risk_score=90.0,
            distance_score=75.0,
            observation_version="obs-1",
            policy_version="v1",
        ),
        StudentHouseScoreSummary(
            house_platform_id=2,
            base_total_score=40.0,
            price_score=40.0,
            option_score=45.0,
            risk_score=55.0,
            distance_score=30.0,
            observation_version="obs-1",
            policy_version="v1",
        ),
    ]

    class FakeFinderRequestRepository:
        def __init__(self, request: FinderRequest):
            self._request = request

        def find_by_id(self, finder_request_id: int):
            if finder_request_id == self._request.finder_request_id:
                return self._request
            return None

    service = RecommendStudentHouseUseCase(
        finder_request_repo=FakeFinderRequestRepository(finder_request),
        house_platform_repo=FakeHousePlatformRepository(),
        observation_repo=FakeObservationRepository(observations),
        score_repo=FakeScoreRepository(scores),
        price_observation_repo=FakePriceObservationRepository(price_observations),
        distance_observation_repo=FakeDistanceObservationRepository(distance_observations),
        policy=DecisionPolicyConfig(),
    )

    result = service.execute(
        RecommendStudentHouseCommand(
            finder_request_id=10,
            candidate_house_platform_ids=candidate_ids,
        )
    )
    print(result)
    assert result is not None
    assert result.finder_request_id == 10
    assert result.status == "SUCCESS"
    assert result.detail is None
    assert result.summary["recommended_count"] == 1
    assert result.summary["rejected_count"] == 1

    recommended = result.recommended_top_k[0]
    rejected = result.rejected_top_k[0]
    assert recommended["decision_status"] == "RECOMMENDED"
    assert rejected["decision_status"] == "REJECTED"

    raw_keys = set(recommended["raw"].keys())
    assert raw_keys == set(HOUSE_PLATFORM_COLUMNS)


def test_recommend_student_house_mock_response():
    candidate_ids = [1, 2, 3]
    candidates = [
        type(
            "Candidate",
            (),
            {
                "house_platform_id": house_platform_id,
                "deposit": 100 * house_platform_id,
                "monthly_rent": 50,
                "manage_cost": 5,
                "snapshot_id": f"snap-{house_platform_id}",
            },
        )()
        for house_platform_id in candidate_ids
    ]

    class FakeFinderRequestRepository:
        def find_by_id(self, _finder_request_id):
            return None

    mock_service = RecommendStudentHouseMockService(
        finder_request_repo=FakeFinderRequestRepository(),
        house_platform_repo=FakeHousePlatformRepository(),
        observation_repo=FakeObservationRepository({}),
        score_repo=FakeScoreRepository([]),
        policy=DecisionPolicyConfig(),
    )

    response = mock_service.execute(
        RecommendStudentHouseMockCommand(
            finder_request_id=999,
            candidates=candidates,
        )
    )
    result = response.to_result()
    assert result.status == "SUCCESS"
    assert result.recommended_top_k
    assert result.rejected_top_k is not None
    assert result.summary["total_candidates"] == len(candidates)
