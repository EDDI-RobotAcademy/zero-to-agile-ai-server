import os

from openai import OpenAI

from modules.chatbot.application.port_out.llm_port import LLMPort


class OpenAIChatAdapter(LLMPort):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        self._model = model or os.getenv("LLM_MODEL")
        if not self._model:
            raise ValueError("LLM_MODEL is not set")

        self._client = OpenAI(api_key=self._api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        return response.choices[0].message.content or ""
