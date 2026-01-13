from modules.ai_explanation.application.dto.finder_explanation_dto import (
    ExplanationInput, ExplanationResult, ReasonItem
)


class ExplainFinderUseCase:
    def execute(self, input_data: ExplanationInput) -> ExplanationResult:
        result = ExplanationResult()

        # 1. 월세 비교 로직
        if input_data.budget_monthly_max:
            # 예산보다 싸면 칭찬
            if input_data.house_monthly_rent <= input_data.budget_monthly_max:
                diff = input_data.budget_monthly_max - input_data.house_monthly_rent
                result.recommended_reasons.append(ReasonItem(
                    code="AFFORDABLE_RENT",
                    text=f"예산보다 {diff}만원 저렴하여 가격 메리트가 있습니다.",
                    evidence={"rent": input_data.house_monthly_rent}
                ))
            # 예산 초과면 경고 (필요 시)
            else:
                result.reject_reasons.append(ReasonItem(
                    code="OVER_BUDGET",
                    text="월세 예산을 초과했습니다.",
                    evidence={"rent": input_data.house_monthly_rent}
                ))

        # 2. 거리 비교 로직
        if input_data.house_distance_min <= 20:  # 20분 이내면 가깝다고 판단
            result.recommended_reasons.append(ReasonItem(
                code="GOOD_LOCATION",
                text=f"학교까지 약 {int(input_data.house_distance_min)}분 거리로 통학이 편리합니다.",
                evidence={"distance": input_data.house_distance_min}
            ))

        return result