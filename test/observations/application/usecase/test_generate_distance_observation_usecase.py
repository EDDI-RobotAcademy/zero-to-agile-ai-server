import pytest
from dataclasses import dataclass

from modules.observations.application.usecase.generate_distance_observation_usecase import (
    GenerateDistanceObservationUseCase,
)
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation


# =========================
# Fake / Stub Models
# =========================

@dataclass
class FakeHouse:
    lat_lng: dict


@dataclass
class FakeBundle:
    house_platform: FakeHouse


@dataclass
class FakeUniversity:
    university_location_id: int
    lat: float
    lng: float


# =========================
# Fake Repositories
# =========================

class FakeDistanceObservationRepository:
    def __init__(self):
        self.called = False
        self.house_id = None
        self.distances = None

    def save_bulk(self, house_id: int, distances: list[DistanceFeatureObservation]):
        self.called = True
        self.house_id = house_id
        self.distances = distances


class FakeHousePlatformRepository:
    def fetch_bundle_by_id(self, house_id: int):
        return FakeBundle(
            house_platform=FakeHouse(
                lat_lng={"lat": 37.5665, "lng": 126.9780}  # 서울 시청
            )
        )


class FakeUniversityRepository:
    def get_university_locations(self):
        return [
            FakeUniversity(1, 37.5512, 126.9882),
            FakeUniversity(2, 37.5800, 126.9980),
            FakeUniversity(3, 37.6000, 127.0100),
        ]


# =========================
# Test
# =========================

def test_generate_distance_observation_usecase():
    # given
    distance_repo = FakeDistanceObservationRepository()
    house_repo = FakeHousePlatformRepository()
    university_repo = FakeUniversityRepository()

    usecase = GenerateDistanceObservationUseCase(
        distance_observation_repo=distance_repo,
        raw_house_repo=house_repo,
        university_repo=university_repo,
    )

    # when
    usecase.execute(house_id=123)

    # then
    assert distance_repo.called is True
    assert distance_repo.house_id == 123
    assert len(distance_repo.distances) == 3

    for obs in distance_repo.distances:
        assert obs.학교까지_분 > 0
        assert 0 <= obs.거리_백분위 <= 1
        assert obs.거리_버킷 in {
            "0_10분",
            "10_20분",
            "20_30분",
            "30_40분",
            "40분_이상",
        }
        assert 0 <= obs.거리_비선형_점수 <= 1
        assert obs.calculated_at is not None
