from app.retrieval import (
    reciprocal_rank_fusion,
)


def test_reciprocal_rank_fusion():
    keyword_results = [
        {
            "chunk_id": "a",
            "text": "A",
        },
        {
            "chunk_id": "b",
            "text": "B",
        },
        {
            "chunk_id": "c",
            "text": "C",
        },
    ]

    semantic_results = [
        {
            "chunk_id": "b",
            "text": "B",
        },
        {
            "chunk_id": "a",
            "text": "A",
        },
        {
            "chunk_id": "d",
            "text": "D",
        },
    ]

    results = reciprocal_rank_fusion(
        [
            keyword_results,
            semantic_results,
        ]
    )

    assert len(results) == 4

    assert results[0][
        "chunk_id"
    ] in {
        "a",
        "b",
    }

    assert results[0][
        "rrf_score"
    ] > results[-1][
        "rrf_score"
    ]


def test_rrf_rewards_multiple_retrievers():
    keyword_results = [
        {
            "chunk_id": "shared",
        },
        {
            "chunk_id": "keyword-only",
        },
    ]

    semantic_results = [
        {
            "chunk_id": "shared",
        },
        {
            "chunk_id": "semantic-only",
        },
    ]

    results = reciprocal_rank_fusion(
        [
            keyword_results,
            semantic_results,
        ]
    )

    assert (
        results[0]["chunk_id"]
        == "shared"
    )