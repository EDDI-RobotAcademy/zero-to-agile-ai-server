from modules.chatbot.application.dto.chat_prompt_dto import (
    ChatPromptRequestDto,
    ChatPromptResponseDto,
)
from modules.chatbot.application.factory.chat_prompt_factory import (
    build_system_prompt,
    build_user_prompt,
)
from modules.chatbot.application.port_in.chat_prompt_port import ChatPromptPort
from modules.chatbot.application.port_out.llm_port import LLMPort


class GenerateChatResponseUseCase(ChatPromptPort):
    def __init__(self, llm_port: LLMPort) -> None:
        self._llm_port = llm_port

    def execute(self, request: ChatPromptRequestDto) -> ChatPromptResponseDto:
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            listing=request.listing,
            user_prompt=request.user_prompt,
            todo_descriptions=dict(request.todo_descriptions or {}),
        )
        answer = self._llm_port.generate(system_prompt, user_prompt)
        return ChatPromptResponseDto(answer=answer)
