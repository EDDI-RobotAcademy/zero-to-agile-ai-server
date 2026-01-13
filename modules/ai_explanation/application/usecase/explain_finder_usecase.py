from modules.ai_explanation.application.dto.finder_explanation_dto import (
    ExplanationInput, ExplanationResult, ReasonItem
)


class ExplainFinderUseCase:
    """
        Price와 Commute 관측치를 기반으로 추천/거절 사유 텍스트를 생성하는 로직
        """

    def execute(self, input_data: ExplanationInput) -> ExplanationResult:
        constraints = input_data.user_constraints
        obs = input_data.observation_summary

        result = ExplanationResult()

        # 1. 가격(Price) 분석
        self._analyze_price(constraints, obs.price, result)

        # 2. 통학(Commute) 분석
        self._analyze_commute(constraints, obs.commute, result)

        # 상위 3개만 남기기
        result.recommended_reasons = result.recommended_reasons[:3]
        result.reject_reasons = result.reject_reasons[:3]

        return result

    def _analyze_price(self, constraints, price_obs, result: ExplanationResult):
        # [A] 거절 사유: 월세 예산 초과
        if constraints.budget_monthly_max and price_obs.monthly_cost_est > constraints.budget_monthly_max:
            result.reject_reasons.append(ReasonItem(
                code="BUDGET_OVER_MONTHLY",
                text=f"월 비용({int(price_obs.monthly_cost_est)}만원)이 예산을 초과했습니다.",
                evidence={
                    "monthly_cost_est": price_obs.monthly_cost_est,
                    "budget_monthly_max": constraints.budget_monthly_max
                }
            ))
            return

            # [B] 추천 사유: 가격 경쟁력 (상위 30% 이내 or 예산 대비 저렴)
        if price_obs.price_percentile <= 0.3:
            top_percent = int(price_obs.price_percentile * 100)
            result.recommended_reasons.append(ReasonItem(
                # code는 생략 가능하므로 넣지 않아도 됨
                text=f"같은 조건 매물 중 가격이 상위 {top_percent}%로 매우 저렴합니다.",
                evidence={
                    "price_percentile": price_obs.price_percentile,
                    "monthly_cost_est": price_obs.monthly_cost_est
                }
            ))
        elif constraints.budget_monthly_max and price_obs.monthly_cost_est <= constraints.budget_monthly_max - 5:
            diff = constraints.budget_monthly_max - price_obs.monthly_cost_est
            result.recommended_reasons.append(ReasonItem(
                text=f"설정하신 예산보다 월 {int(diff)}만원 절약할 수 있습니다.",
                evidence={
                    "monthly_cost_est": price_obs.monthly_cost_est,
                    "budget_diff": diff
                }
            ))

    def _analyze_commute(self, constraints, commute_obs, result: ExplanationResult):
        # [A] 거절 사유: 통학 시간 초과
        if constraints.max_commute_min and commute_obs.distance_to_school_min > constraints.max_commute_min:
            result.reject_reasons.append(ReasonItem(
                code="COMMUTE_OVER_LIMIT",
                text=f"희망 통학 시간({constraints.max_commute_min}분)을 초과했습니다.",
                evidence={
                    "distance_to_school_min": commute_obs.distance_to_school_min,
                    "max_commute_min": constraints.max_commute_min
                }
            ))
            return

        # [B] 추천 사유: 통학 거리 우수 (20분 이내)
        if commute_obs.distance_to_school_min <= 20:
            result.recommended_reasons.append(ReasonItem(
                text=f"학교까지 약 {int(commute_obs.distance_to_school_min)}분 거리로 통학이 편리합니다.",
                evidence={
                    "distance_to_school_min": commute_obs.distance_to_school_min,
                    "distance_bucket": commute_obs.distance_bucket
                }
            ))