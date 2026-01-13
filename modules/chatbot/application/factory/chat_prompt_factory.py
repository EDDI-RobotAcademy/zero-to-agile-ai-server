from __future__ import annotations

from typing import Iterable

from modules.chatbot.application.dto.chat_prompt_dto import ChatListingDto


# chat_prompt_factory.py

SYSTEM_PROMPT = "\n".join(
    [
        "너는 부동산 매물 요약 어시스턴트다.",
        "입력 JSON에는 반드시 `listing`과 `userPrompt`가 들어온다.",
        "너는 오직 입력으로 주어진 `listing`과 `userPrompt`의 정보만 사용해야 하며,",
        "없는 정보는 절대 추측하지 말고 \"정보 없음(확인 필요)\"로 명시한다.",
        "답변은 친절하게 답한다."
        "[출력 내용 금지 규칙 - 매우 중요]",
        "- \"근거\", \"필드\", \"필드명\", \"source\", \"참고\", \"based on\", \"(근거: ...)\" 같은 근거 표기를 절대 출력하지 않는다.",
        "- `listing.images`는 절대 언급하지 않는다. (개수/URL/사진 제공 여부 모두 출력 금지)",
        "",
        "[전문용어 표기 규칙]",
        "- 전문용어(technical term)가 나오면 처음 등장 시 괄호로 간단 정의를 붙인다.",
        "  예: 역세권(지하철역 도보 접근성이 좋은 입지), 관리비(공용관리/시설유지 비용)",
        "",
        "[비용/단위 규칙]",
        "- `salesType`, `price`, `monthlyRent`, `manageCost`는 값이 있으면 정리하되,",
        "  단위는 만원 단위 이다.",
        "- 추가 계산(연환산, 총비용 산출, 주변 시세 비교 등)은 하지 않는다.",
        "",
        # ✅ 여기부터 추가 (핵심)
        "[사용자 질문 우선 규칙 - 매우 중요]",
        "- 반드시 먼저 사용자 질문(userPrompt)에 대한 '직접 답변'을 최우선으로 제공한다.",
        "- userPrompt가 특정 값(예: 관리비/보증금/월세/면적/층수 등)을 묻는 질문이면,",
        "  해당 값 + \"단위 미제공(확인 필요)\" 여부만 간단히 답하고, 종합 요약/장단점은 최소화한다.",
        "- userPrompt가 \"요약해줘\", \"장단점 알려줘\"처럼 종합 정리를 요구할 때만 상세 섹션을 확장한다.",
        "",
        "[출력 구조 - JSON으로만 출력]",
        "- 단일 질문(예: 관리비 얼마야)에는 질문에 대한 답변을 친절히 답변하고 아래의 형식을 사용한다.",
        "답변 : "
        "- 종합 요약 요청일 때만 아래 순서의 형식을 사용한다.",
        "  1) 요약",
        "  2) 장점",
        "  3) 단점/주의사항",
        "  4) 추가 확인 체크리스트",
        "",
        "이제 `userPrompt`의 요구에 맞춰 위 규칙대로 JSON으로만 답변하라.",
    ]
)



def build_system_prompt() -> str:
    return SYSTEM_PROMPT


def build_user_prompt(
    listing: ChatListingDto,
    user_prompt: str,
    todo_descriptions: dict[str, str] | None,
) -> str:
    lines: list[str] = [
        "다음은 부동산 매물 정보이다.",
        "",
        "[사용자 요청]",
        user_prompt,
        "",
        "[매물 정보]",
        f"- title: {listing.title}",
        f"- description: {listing.description}",
        f"- type: {listing.type}",
        f"- images: {format_items(listing.images)}",
        f"- salesType: {listing.sales_type}",
        f"- price: {listing.price}",
        f"- monthlyRent: {listing.monthly_rent}",
        f"- manageCost: {listing.manage_cost}",
        f"- area: {listing.area}",
        f"- floor: {listing.floor}",
        f"- allFloors: {listing.all_floors}",
        f"- hasElevator: {listing.has_elevator}",
        f"- canPark: {listing.can_park}",
        f"- rank: {listing.rank}",
        f"- matchScore: {listing.match_score}",
        f"- options: {format_items(listing.options)}",
        f"- aiReasons: {format_items(listing.ai_reasons)}",
        "",
        "[리스크]",
        f"- riskLevel: {listing.risk_level}",
        f"- riskDescription: {listing.risk_description}",
        "- riskFlags:",
    ]

    if listing.risk_flags:
        for flag in listing.risk_flags:
            lines.append(f"  - severity: {flag.severity}, message: {flag.message}")
    else:
        lines.append("  - (없음)")

    if todo_descriptions:
        lines.extend(
            [
                "",
                "[TODO: 컬럼 설명]",
            ]
        )
        for key, value in todo_descriptions.items():
            lines.append(f"- {key}: TODO {value}")

    return "\n".join(lines).strip()


def format_items(items: Iterable[str]) -> str:
    return ", ".join(items) if items else "-"
