from __future__ import annotations

HOUSE_TYPE_MAP = {
    "apartment": "아파트",
    "officetel": "오피스텔",
    "villa": "빌라",
    "house": "단독주택",
    "commercial": "상가",
}


def normalize_house_type_tokens(raw: str | None) -> list[str]:
    """house_type 입력을 필터링용 토큰으로 정규화한다."""
    if not raw:
        return []
    token = raw.strip()
    if not token:
        return []

    lowered = token.lower()
    mapped = HOUSE_TYPE_MAP.get(lowered)
    if mapped:
        tokens = [mapped]
        if token != mapped:
            tokens.append(token)
        return _unique(tokens)

    if token in HOUSE_TYPE_MAP.values():
        return [token]

    return [token]


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
