
from modules.house_platform.application.dto.house_platform_dto import (
    HousePlatformUpsertModel,
    HousePlatformOptionUpsertModel,
)
from modules.observations.application.assembler.observation_raw_assembler import ObservationRawAssembler


def test_build_price_raw():
    house = HousePlatformUpsertModel(
        deposit=1000,
        monthly_rent=50,
        manage_cost=10,
    )

    result = ObservationRawAssembler.build_price_raw(house)

    assert result["expected_move_in_cost"] == 1000
    assert result["monthly_cost_estimate"] == 60
    assert result["price_percentile"] is None
    assert result["price_zscore"] is None
    assert result["nonlinear_price_burden"] is None


def test_build_convenience_raw():
    options = HousePlatformOptionUpsertModel(
        built_in=True,
        near_univ=True,
        near_transport=False,
        near_mart=False,
    )

    result = ObservationRawAssembler.build_convenience_raw(options)

    assert result["essential_option_coverage"] == 0.5
    assert result["convenience_score"] == 0.5


def test_build_distance_raw():
    result = ObservationRawAssembler.build_distance_raw(
        minutes_to_school=9,
        distance_bucket="5-10",
        distance_percentile=0.7,
    )

    assert result["minutes_to_school"] == 9
    assert result["distance_bucket"] == "5-10"
    assert result["distance_percentile"] == 0.7
    assert result["nonlinear_distance_score"] == 1 / 10

def test_build_risk_raw():
    house = HousePlatformUpsertModel(
        is_banned=True,
        floor_no=2,
        all_floors=10,
        lat_lng={"lat": 37.5, "lng": 127.0},
        gu_nm="강남구",
    )

    result = ObservationRawAssembler.build_risk_raw(house)

    assert result["is_banned"] is True
    assert result["floor_ratio"] == 0.2
    assert result["has_location"] is True
    assert result["region_code"] == "강남구"
