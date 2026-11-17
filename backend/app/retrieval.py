from collections import defaultdict
from typing import Any


DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict[str, Any]]],
    *,
    key: str = "chunk_id",
    k: int = DEFAULT_RRF_K,
) -> list[dict[str, Any]]:
    scores: dict[str, float] = defaultdict(float)
    items: dict[str, dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(
            ranked_list,
            start=1,
        ):
            item_key = str(item[key])

            scores[item_key] += 1.0 / (
                k + rank
            )

            if item_key not in items:
                items[item_key] = dict(item)

    fused_results = []

    for item_key, item in items.items():
        result = dict(item)

        result["rrf_score"] = scores[
            item_key
        ]

        fused_results.append(result)

    fused_results.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return fused_results