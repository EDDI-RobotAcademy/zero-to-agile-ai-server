# test_generate_full_observation_usecase.py
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from modules.observations.application.usecase.generate_distance_observation_usecase import \
    GenerateDistanceObservationUseCase
from modules.observations.application.usecase.generate_price_observation_usecase import GeneratePriceObservationUseCase
from modules.observations.application.usecase.generate_student_recommendation_feature_observation_usecase import \
    GenerateStudentRecommendationFeatureObservationUseCase
from modules.observations.application.usecase.generate_full_observation_usecase import GenerateFullObservationUseCase
from modules.observations.domain.model.student_recommendation_feature_observation import \
    StudentRecommendationFeatureObservation
from modules.observations.application.assembler.observation_raw_assembler import ObservationRawAssembler


# ----------------- Mock DTOs -----------------
class MockHouse:
    def __init__(self):
        self.lat_lng = {"lat": 37.5, "lng": 127.0}
        self.deposit = 1000
        self.monthly_rent = 500
        self.manage_cost = 50
        self.is_banned = False
        self.floor_no = 3
        self.all_floors = 10
        self.gu_nm = "TestGu"
        self.snapshot_id = "snapshot_1"
        self.data_version = "v1.0"


class MockBundle:
    def __init__(self):
        self.house_platform = MockHouse()
        self.options = MagicMock(built_in=True, near_univ=True, near_transport=True, near_mart=True)


class MockUniversity:
    def __init__(self, uid, lat, lng):
        self.university_location_id = uid
        self.lat = lat
        self.lng = lng


class MockUniversityRepo:
    def get_university_locations(self):
        # 테스트용 614개 대학
        return [MockUniversity(uid=i, lat=37.5 + i * 0.001, lng=127.0 + i * 0.001) for i in range(614)]


# ----------------- Test -----------------
def test_full_observation_orchestration():
    # --- Repository Mocks ---
    mock_obs_repo = MagicMock()
    mock_obs_repo.save.side_effect = lambda feature: type(feature)(**{**feature.__dict__, "id": 1})

    mock_distance_repo = MagicMock()
    mock_distance_repo.save_bulk.side_effect = lambda vos: vos

    mock_price_repo = MagicMock()
    mock_price_repo.save.side_effect = lambda vo: vo

    mock_house_repo = MagicMock()
    mock_bundle = MockBundle()
    mock_house_repo.fetch_bundle_by_id.return_value = mock_bundle

    mock_university_repo = MockUniversityRepo()

    # --- UseCase 구성 ---
    distance_uc = GenerateDistanceObservationUseCase(
        distance_repo=mock_distance_repo,
        house_repo=mock_house_repo,
        university_repo=mock_university_repo,
    )

    price_uc = GeneratePriceObservationUseCase(
        price_repo=mock_price_repo,
        house_prices={1: 1000}  # house_id -> price
    )

    student_feature_uc = GenerateStudentRecommendationFeatureObservationUseCase(
        observation_repo=mock_obs_repo,
        distance_usecase=None,  # Orchestrator에서 처리
        house_repo=mock_house_repo
    )

    full_uc = GenerateFullObservationUseCase(
        student_feature_uc=student_feature_uc,
        price_uc=price_uc,
        distance_uc=distance_uc
    )

    # --- Execute ---
    student_feature: StudentRecommendationFeatureObservation = full_uc.execute(house_id=1)

    # --- Assertions ---
    assert student_feature.id == 1
    assert student_feature.house_platform_id == 1
    assert hasattr(student_feature, "위험_관측치")
    assert hasattr(student_feature, "편의_관측치")

    # DistanceObservation 614개 저장 확인
    assert mock_distance_repo.save_bulk.call_count == 1
    saved_distances = mock_distance_repo.save_bulk.call_args[0][0]
    assert len(saved_distances) == 614

    # PriceObservation 저장 확인
    assert mock_price_repo.save.call_count == 1

