from app.embeddings import embed_text


def test_embed_text_returns_expected_dimensions():
    embedding = embed_text(
        "ResearchForge semantic search test."
    )

    assert isinstance(
        embedding,
        list,
    )

    assert len(embedding) == 384

    assert all(
        isinstance(value, float)
        for value in embedding
    )