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
        system_prompt = f"당신은 자취방 구해주는 AI입니다. 말투: {tone}"
        user_prompt = f"이 매물들이 왜 좋은지 설명해줘:\n{item_desc}\n추가요청: {user_message or '없음'}"

        return self._call_openai(system_prompt, user_prompt)

    def generate_owner_explanation(self, house, tenant, tone) -> str:
        if not self._client: return "AI 서비스를 사용할 수 없습니다."

        system_prompt = f"당신은 임대 관리 전문가입니다. 말투: {tone}"
        user_prompt = (
            f"내 집: {house.title} (월세 {house.monthly_rent})\n"
            f"세입자: {tenant.job_status}, 예산 {tenant.budget_monthly}, 특징 {tenant.lifestyle_tags}\n"
            "이 세입자를 추천하는 이유를 설명해줘."
        )

        return self._call_openai(system_prompt, user_prompt)

    def _call_openai(self, system, user):
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return "일시적인 오류로 설명을 생성하지 못했습니다."