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

    def generate_owner_explanation(self, request_data) -> str:

        tone_str = request_data.tone.value
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
                위 매칭 포인트를 근거로, 이 세입자를 놓치면 안 되는 이유를 정중하게({tone_str}) 3문장으로 설득해 주세요.
                """

        return self._call_openai("당신은 부동산 전문가입니다.", prompt)

    def _call_openai(self, system_role: str, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        model_name = os.getenv("LLM_MODEL", "gpt-4o").strip()

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content