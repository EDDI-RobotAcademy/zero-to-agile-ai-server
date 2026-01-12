from fastapi import APIRouter, HTTPException, status
from starlette.responses import JSONResponse

from modules.chatbot.adapter.input.web.request.chat_prompt_request import (
    ChatPromptRequest,
    ListingRequest,
    RiskFlagRequest,
)
from modules.chatbot.adapter.input.web.response.chat_prompt_response import (
    ChatPromptResponse,
)
from modules.chatbot.adapter.output.openai_chat_adapter import OpenAIChatAdapter
from modules.chatbot.application.dto.chat_prompt_dto import (
    ChatListingDto,
    ChatPromptRequestDto,
    RiskFlagDto,
)
from modules.chatbot.application.factory.chat_prompt_factory import (
    build_system_prompt,
    build_user_prompt,
)
from modules.chatbot.application.usecase.generate_chat_response_usecase import (
    GenerateChatResponseUseCase,
)
from shared.common.utils.token_counter import count_tokens
from shared.infrastructure.config.llm_config import LLM_MODEL, MAX_PROMPT_TOKENS

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def _to_listing_dto(request: ListingRequest) -> ChatListingDto:
    return ChatListingDto(
        title=request.title,
        description=request.description,
        type=request.type,
        images=request.images,
        sales_type=request.sales_type,
        price=request.price,
        monthly_rent=request.monthly_rent,
        manage_cost=request.manage_cost,
        area=request.area,
        floor=request.floor,
        all_floors=request.all_floors,
        has_elevator=request.has_elevator,
        can_park=request.can_park,
        rank=request.rank,
        match_score=request.match_score,
        options=request.options,
        ai_reasons=request.ai_reasons,
        risk_level=request.risk_level,
        risk_flags=[
            RiskFlagDto(severity=flag.severity, message=flag.message)
            for flag in request.risk_flags
        ],
        risk_description=request.risk_description,
    )


def _mock_request() -> ChatPromptRequest:
    return ChatPromptRequest(
        listing=ListingRequest(
            title="강남역 도보 7분 신축 오피스텔",
            description="남향, 풀옵션, 즉시 입주 가능. 2년 내 신축, 관리 상태 양호.",
            type="officetel",
            images=[
                "https://example.com/images/officetel-1.jpg",
                "https://example.com/images/officetel-2.jpg",
            ],
            sales_type="monthly",
            price=10000000,
            monthly_rent=75,
            manage_cost=10,
            area=24.3,
            floor=7,
            all_floors=15,
            has_elevator=True,
            can_park=False,
            rank=1,
            match_score=0.86,
            options=["에어컨", "세탁기", "냉장고", "붙박이장"],
            ai_reasons=["역세권 접근성 우수", "신축으로 시설 상태가 좋음"],
            risk_level="medium",
            risk_flags=[
                RiskFlagRequest(severity="medium", message="주차 공간이 부족함"),
            ],
            risk_description="자차 이용 시 주차 여유가 부족할 수 있음",
        ),
        user_prompt="이 매물의 장단점과 주의사항을 요약해줘.",
    )


@router.post("/prompt", response_model=ChatPromptResponse)
def generate_response(request: ChatPromptRequest) -> ChatPromptResponse:
    listing = _to_listing_dto(request.listing)
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(
        listing=listing,
        user_prompt=request.user_prompt,
        todo_descriptions=request.todo_descriptions,
    )
    token_count = count_tokens(f"{system_prompt}\n\n{user_prompt}", LLM_MODEL)
    if token_count > MAX_PROMPT_TOKENS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"answer": "너 말이 너무 많아 짧게 말해"},
        )

    usecase = GenerateChatResponseUseCase(llm_port=OpenAIChatAdapter())
    result = usecase.execute(
        ChatPromptRequestDto(
            listing=listing,
            user_prompt=request.user_prompt,
            todo_descriptions=request.todo_descriptions,
        )
    )
    return ChatPromptResponse(answer=result.answer)


@router.post("/prompt/mock", response_model=ChatPromptResponse)
def generate_response_with_mock() -> ChatPromptResponse:
    mock_request = _mock_request()
    listing = _to_listing_dto(mock_request.listing)
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(
        listing=listing,
        user_prompt=mock_request.user_prompt,
        todo_descriptions=mock_request.todo_descriptions,
    )
    token_count = count_tokens(f"{system_prompt}\n\n{user_prompt}", LLM_MODEL)
    print("토큰 카운트 : "+str(token_count))
    if token_count > MAX_PROMPT_TOKENS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"answer": "너 말이 너무 많아 짧게 말해"},
        )

    usecase = GenerateChatResponseUseCase(llm_port=OpenAIChatAdapter())
    result = usecase.execute(
        ChatPromptRequestDto(
            listing=listing,
            user_prompt=mock_request.user_prompt,
            todo_descriptions=mock_request.todo_descriptions,
        )
    )
    return ChatPromptResponse(answer=result.answer)
