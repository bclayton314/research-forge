def normalize_text(text: str) -> str:
    return "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative"
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    normalized = normalize_text(text)

    if not normalized:
        return []

    chunks = []
    start = 0

    while start < len(normalized):
        end = min(
            start + chunk_size,
            len(normalized),
        )

        chunk = normalized[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(normalized):
            break

        start = end - overlap

    return chunks