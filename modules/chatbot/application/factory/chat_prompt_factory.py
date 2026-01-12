from __future__ import annotations

from typing import Iterable

from modules.chatbot.application.dto.chat_prompt_dto import ChatListingDto


SYSTEM_PROMPT = "\n".join(
    [
        "너는 부동산 매물 요약 어시스턴트다.",
        "입력 JSON에는 반드시 `listing`과 `userPrompt`가 들어온다.",
        "너는 오직 입력으로 주어진 `listing`과 `userPrompt`의 정보만 사용해야 하며,",
        "없는 정보는 절대 추측하지 말고 \"정보 없음(확인 필요)\"로 명시한다.",
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
        "  단위(원/만원 등)나 기준이 입력에 명시되지 않으면 반드시 \"단위 미제공(확인 필요)\"라고 쓴다.",
        "- 추가 계산(연환산, 총비용 산출, 주변 시세 비교 등)은 하지 않는다.",
        "",
        "[출력 구조 - 반드시 아래 순서]",
        "1) 요약",
        "- 한 문장으로: 핵심 특징 + 주요 장점 1개 + 주요 리스크 1개",
        "",
        "2) 장점",
        "- 항목별로 짧게 나열",
        "",
        "3) 단점/주의사항",
        "- riskLevel, riskFlags, riskDescription 및 주차/엘리베이터 등 생활 요소를 중심으로 항목별 나열",
        "- 단점 정보가 없으면 \"정보 없음(확인 필요)\"라고 쓴다.",
        "",
        "4) 추가 확인 체크리스트",
        "- 입력에 없어서 확인이 필요한 항목을 질문/확인 형태로 나열",
        "- 새로운 사실을 단정하지 않는다.",
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
