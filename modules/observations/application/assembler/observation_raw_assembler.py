from typing import Iterable

from modules.house_platform.application.dto.house_platform_dto import HousePlatformUpsertModel, \
    HousePlatformOptionUpsertModel
from modules.observations.domain.model.distance_feature_observation import DistanceFeatureObservation


class ObservationRawAssembler:
    @staticmethod
    def build_price_raw(
            house: HousePlatformUpsertModel,
    ) -> dict:
        total_monthly_cost = (
                (house.monthly_rent or 0)
                + (house.manage_cost or 0)
        )

        return {
            "price_percentile": None,  # 외부 통계 주입
            "price_zscore": None,  # 외부 통계 주입
            "expected_move_in_cost": house.deposit or 0,
            "monthly_cost_estimate": total_monthly_cost,
            "nonlinear_price_burden": None,  # 후처리
        }

    @staticmethod
    def build_convenience_raw(
            options: HousePlatformOptionUpsertModel,
    ) -> dict:
        coverage = sum([
            bool(options.built_in),
            options.near_univ,
            options.near_transport,
            options.near_mart,
        ]) / 4.0

        return {
            "essential_option_coverage": coverage,
            "convenience_score": coverage,
        }

    @staticmethod
    def empty_convenience_raw() -> dict:
        """
        House 옵션이 없을 때 사용.
        필수 옵션 커버리지와 편의 점수를 0으로 반환.
        """
        return {
            "essential_option_coverage": 0.0,
            "convenience_score": 0.0,
        }

    @staticmethod
    def build_distance_summary_raw(
            distances: Iterable[DistanceFeatureObservation],
    ) -> dict:
        """
        614개 DistanceObservation 중
        FeatureObservation에 들어갈 대표 요약값 생성
        """

        if not distances:
            return {
                "minutes_to_school": None,
                "distance_bucket": "UNKNOWN",
                "distance_percentile": None,
                "nonlinear_distance_score": None,
            }

        # 최소 이동 시간 기준
        closest = min(distances, key=lambda d: d.학교까지_분)

        return {
            "minutes_to_school": closest.학교까지_분,
            "distance_bucket": closest.거리_버킷,
            "distance_percentile": closest.거리_백분위,
            "nonlinear_distance_score": closest.거리_비선형_점수,
        }

    @staticmethod
    def build_risk_raw(
            house: HousePlatformUpsertModel,
    ) -> dict:
        return {
            "is_banned": bool(house.is_banned),
            "floor_ratio": (
                house.floor_no / house.all_floors
                if house.floor_no and house.all_floors
                else None
            ),
            "has_location": house.lat_lng is not None,
            "region_code": house.gu_nm,
        }
