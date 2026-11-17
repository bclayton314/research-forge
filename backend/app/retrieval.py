from collections import defaultdict
from typing import Any
from sqlalchemy import or_
from .embeddings import embed_text
from .extensions import db
from .models import Document, DocumentChunk
from .search import (
    make_snippet,
    parse_query,
    score_text,
)


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


def retrieve_keyword_results(
    query: str,
    limit: int = 20,
) -> list[dict]:
    terms = parse_query(query)

    if not terms:
        return []

    conditions = [
        DocumentChunk.text.ilike(
            f"%{term}%"
        )
        for term in terms
    ]

    rows = (
        db.session.execute(
            db.select(
                DocumentChunk,
                Document,
            )
            .join(
                Document,
                DocumentChunk.document_id
                == Document.id,
            )
            .where(
                or_(*conditions)
            )
        )
        .all()
    )

    results = []

    for chunk, document in rows:
        score = score_text(
            chunk.text,
            terms,
        )

        results.append(
            {
                "document_id": str(
                    document.id
                ),
                "document_name":
                    document.original_filename,
                "chunk_id": str(
                    chunk.id
                ),
                "chunk_index":
                    chunk.chunk_index,
                "keyword_score": score,
                "text": chunk.text,
                "snippet": make_snippet(
                    chunk.text,
                    terms,
                ),
            }
        )

    results.sort(
        key=lambda result:
            result["keyword_score"],
        reverse=True,
    )

    return results[:limit]


def retrieve_semantic_results(
    query: str,
    limit: int = 20,
) -> list[dict]:
    query_embedding = embed_text(query)

    distance = (
        DocumentChunk.embedding
        .cosine_distance(
            query_embedding
        )
    )

    rows = (
        db.session.execute(
            db.select(
                DocumentChunk,
                Document,
                distance.label(
                    "distance"
                ),
            )
            .join(
                Document,
                DocumentChunk.document_id
                == Document.id,
            )
            .where(
                DocumentChunk.embedding
                .is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )
        .all()
    )

    results = []

    for (
        chunk,
        document,
        cosine_distance,
    ) in rows:
        similarity = (
            1.0
            - float(cosine_distance)
        )

        results.append(
            {
                "document_id": str(
                    document.id
                ),
                "document_name":
                    document.original_filename,
                "chunk_id": str(
                    chunk.id
                ),
                "chunk_index":
                    chunk.chunk_index,
                "semantic_score":
                    similarity,
                "text": chunk.text,
            }
        )

    return results


def hybrid_search(
    query: str,
    *,
    limit: int = 10,
    candidate_limit: int = 20,
) -> list[dict]:
    keyword_results = (
        retrieve_keyword_results(
            query,
            limit=candidate_limit,
        )
    )

    semantic_results = (
        retrieve_semantic_results(
            query,
            limit=candidate_limit,
        )
    )

    fused = reciprocal_rank_fusion(
        [
            keyword_results,
            semantic_results,
        ]
    )

    keyword_by_id = {
        result["chunk_id"]: result
        for result in keyword_results
    }

    semantic_by_id = {
        result["chunk_id"]: result
        for result in semantic_results
    }

    final_results = []

    for result in fused[:limit]:
        chunk_id = result["chunk_id"]

        keyword_result = (
            keyword_by_id.get(
                chunk_id
            )
        )

        semantic_result = (
            semantic_by_id.get(
                chunk_id
            )
        )

        result["keyword_score"] = (
            keyword_result[
                "keyword_score"
            ]
            if keyword_result
            else None
        )

        result["semantic_score"] = (
            semantic_result[
                "semantic_score"
            ]
            if semantic_result
            else None
        )

        result["matched_keyword"] = (
            keyword_result is not None
        )

        result["matched_semantic"] = (
            semantic_result is not None
        )

        final_results.append(
            result
        )

    return final_results
