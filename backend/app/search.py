import re


WORD_PATTERN = re.compile(r"\b[\w'-]+\b")


def parse_query(query: str) -> list[str]:
    return [
        word.lower()
        for word in WORD_PATTERN.findall(query)
        if word.strip()
    ]


def score_text(
    text: str,
    terms: list[str],
) -> int:
    normalized_text = text.lower()

    return sum(
        normalized_text.count(term)
        for term in terms
    )


def make_snippet(
    text: str,
    terms: list[str],
    max_length: int = 300,
) -> str:
    if len(text) <= max_length:
        return text

    normalized_text = text.lower()

    positions = [
        normalized_text.find(term)
        for term in terms
        if normalized_text.find(term) >= 0
    ]

    if not positions:
        return text[:max_length].strip()

    first_match = min(positions)

    half_window = max_length // 2

    start = max(
        0,
        first_match - half_window,
    )

    end = min(
        len(text),
        start + max_length,
    )

    snippet = text[start:end].strip()

    if start > 0:
        snippet = f"...{snippet}"

    if end < len(text):
        snippet = f"{snippet}..."

    return snippet