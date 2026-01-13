from modules.observations.application.usecase.generate_distance_observation_usecase import \
    GenerateDistanceObservationUseCase
from modules.observations.application.usecase.generate_price_observation_usecase import GeneratePriceObservationUseCase
from modules.observations.application.usecase.generate_student_recommendation_feature_observation_usecase import \
    GenerateStudentRecommendationFeatureObservationUseCase


class GenerateFullObservationUseCase:

    def __init__(
        self,
        student_feature_uc: GenerateStudentRecommendationFeatureObservationUseCase,
        price_uc: GeneratePriceObservationUseCase,
        distance_uc: GenerateDistanceObservationUseCase,
    ):
        self.student_feature_uc = student_feature_uc
        self.price_uc = price_uc
        self.distance_uc = distance_uc

    def execute(self, house_id: int):
        # 1. 학생 추천 Feature 생성
        student_feature = self.student_feature_uc.execute(house_id)

        # 2. PriceObservation 생성
        self.price_uc.execute(
            recommendation_observation_id=student_feature.id,
            house_platform_id=house_id
        )

        # 3. DistanceObservation 생성
        self.distance_uc.execute(
            recommendation_observation_id=student_feature.id,
            house_id=house_id
        )

        return student_feature
