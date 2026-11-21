from typing import Any

from .llm import generate_grounded_answer
from .retrieval import hybrid_search


DEFAULT_CONTEXT_RESULTS = 5


def build_context(
    results: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    context_parts = []
    sources = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        source_label = f"Source {index}"

        document_name = result[
            "document_name"
        ]

        chunk_index = result[
            "chunk_index"
        ]

        text = result["text"]

        context_parts.append(
            (
                f"[{source_label}]\n"
                f"Document: {document_name}\n"
                f"Chunk: {chunk_index + 1}\n"
                f"{text}"
            )
        )

        sources.append(
            {
                "label": source_label,
                "document_id": (
                    result["document_id"]
                ),
                "document_name": (
                    document_name
                ),
                "chunk_id": (
                    result["chunk_id"]
                ),
                "chunk_index": (
                    chunk_index
                ),
                "rrf_score": (
                    result["rrf_score"]
                ),
            }
        )

    return (
        "\n\n---\n\n".join(
            context_parts
        ),
        sources,
    )


def answer_question(
    question: str,
    *,
    limit: int = DEFAULT_CONTEXT_RESULTS,
) -> dict[str, Any]:
    retrieval_results = hybrid_search(
        question,
        limit=limit,
    )

    if not retrieval_results:
        return {
            "question": question,
            "answer": (
                "The available documents do not "
                "provide enough information to "
                "answer this question."
            ),
            "sources": [],
        }

    context, sources = build_context(
        retrieval_results
    )

    answer = generate_grounded_answer(
        question,
        context,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }