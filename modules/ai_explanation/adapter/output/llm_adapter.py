import os
from openai import OpenAI
from modules.ai_explanation.application.port.llm_port import LLMPort


class LLMAdapter(LLMPort):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._client = OpenAI(api_key=self._api_key)
        self._model = model or os.getenv("LLM_MODEL")

    def generate_finder_explanation(self, items, user_message, tone) -> str:
        if not self._client: return "AI 서비스를 사용할 수 없습니다."

        # 간단한 프롬프트 구성
        item_desc = "\n".join([f"- {i.title}: {i.deposit}/{i.monthly_rent}, 옵션 {i.options}" for i in items])
        system_prompt = f"당신은 애방의 전문자취방 구해주는 AI입니다. 말투: {tone}"
        user_prompt = f"이 매물들이 왜 좋은지 설명해줘:\n{item_desc}\n추가요청: {user_message or '없음'}"

        return self._call_openai(system_prompt, user_prompt)

    def generate_finder_explanation(self, request_data, tone) -> str:
        """
        request_data는 UseCase에서 넘겨준 FinderExplanationRequest 객체입니다.
        """
        obs = request_data.house_observation
        cons = request_data.user_constraints
        raw = request_data.house_raw

        #  가격 분석 텍스트화
        price_info = f"월 추산 비용 {obs.price.get('monthly_cost_est')}만 원"
        if 'price_percentile' in obs.price:
            # 하위 22% = 상위 22% 저렴
            percentile = float(obs.price['price_percentile']) * 100
            price_info += f" (주변 시세 대비 상위 {percentile:.1f}% 저렴)"

        #  통학 거리 텍스트화
        commute_info = f"학교까지 {obs.commute.get('distance_to_school_min')}분 소요 ({obs.commute.get('distance_bucket')} 구간)"

        prompt = f"""
        [사용자 희망 조건]
        - 예산: 보증금 {cons.budget_deposit_max}, 월세 {cons.budget_monthly_max}
        - 희망 통학 시간: {cons.max_commute_min}분 이내

        [매물 분석 결과 (성적표)]
        - 가격 경쟁력: {price_info}
        - 통학 접근성: {commute_info}
        - 리스크 확률: {obs.risk.get('risk_probability_est', 0)}%
        - 매물 기본 정보: {raw.title}, 보증금 {raw.deposit}/월세 {raw.monthly_rent}

        [지시 사항]
        위 '분석 결과'를 바탕으로 이 매물이 왜 사용자 조건에 딱 맞는지 추천하는 이유를 3줄 이내로 작성해줘.
        말투는 '{tone}'로 하고, 구체적인 수치(예: 상위 22%, 18분 등)를 인용해서 설득력을 높여줘.
        """

        return self._call_openai(
            system_role="당신은 데이터 기반 부동산 분석 전문가입니다.",
            user_prompt=prompt
        )

    def generate_owner_explanation(self, request_data, tone) -> str:

        tone = request_data.tone.value
        owner_house = request_data.owner_house
        finders = request_data.finders

        # 1. 지역 매칭 분석
        region_match = "일치" if owner_house.dong_nm in finders.preferred_region else "인접"

        # 2. 예산 분석
        if finders.max_rent >= owner_house.monthly_rent:
            budget_status = "예산 충분 (월세 지불 능력 우수)"
        else:
            budget_status = f"예산 소폭 부족 (차액 {owner_house.monthly_rent - finders.max_rent}원)"

        # 3. 프롬프트
        prompt = f"""
                [내 매물]
                - 위치: {owner_house.address} ({owner_house.gu_nm} {owner_house.dong_nm})
                - 가격: 보증금 {owner_house.deposit} / 월세 {owner_house.monthly_rent}
                - 타입: {owner_house.residence_type} ({owner_house.room_type})

                [세입자 후보]
                - 희망 지역: {finders.preferred_region}
                - 예산 상한: 월 {finders.max_rent}
                - 희망 타입: {finders.house_type}

                [매칭 포인트]
                - 지역 적합도: {region_match}
                - 예산 안정성: {budget_status}

                [지시 사항]
                당신은 임대인에게 세입자를 추천하는 AI 비서입니다.
                위 매칭 포인트를 근거로, 이 세입자를 놓치면 안 되는 이유를 정중하게({tone}) 3문장으로 설득해 주세요.
                """

        return self._call_openai(..., prompt)