from app.rag import build_context


def test_build_context():
    results = [
        {
            "document_id": "document-1",
            "document_name": "history.pdf",
            "chunk_id": "chunk-1",
            "chunk_index": 2,
            "rrf_score": 0.032,
            "text": (
                "Foreign influence played "
                "an important role."
            ),
        }
    ]

    context, sources = build_context(
        results
    )

    assert "[Source 1]" in context
    assert "history.pdf" in context
    assert "Foreign influence" in context

    assert len(sources) == 1

    assert sources[0]["label"] == "Source 1"
    assert sources[0]["chunk_index"] == 2


def test_ask_question(
    client,
    monkeypatch,
):
    def fake_answer_question(question):
        return {
            "question": question,
            "answer": (
                "Foreign influence was "
                "an important factor."
            ),
            "sources": [
                {
                    "label": "Source 1",
                    "document_id": "document-1",
                    "document_name": "history.pdf",
                    "chunk_id": "chunk-1",
                    "chunk_index": 0,
                    "rrf_score": 0.03,
                }
            ],
        }

    monkeypatch.setattr(
        "app.routes.answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/api/ask",
        json={
            "question": (
                "What caused the unrest?"
            ),
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert (
        data["question"]
        == "What caused the unrest?"
    )

    assert (
        "Foreign influence"
        in data["answer"]
    )

    assert len(data["sources"]) == 1


def test_ask_requires_question(
    client,
):
    response = client.post(
        "/api/ask",
        json={},
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "question is required",
    }


def test_mock_llm_answer(
    monkeypatch,
):
    monkeypatch.setenv(
        "RESEARCHFORGE_MOCK_LLM",
        "true",
    )

    from app.llm import (
        generate_grounded_answer,
    )

    answer = generate_grounded_answer(
        "What happened?",
        (
            "[Source 1]\n"
            "The expedition arrived "
            "in June."
        ),
    )

    assert (
        "Mock ResearchForge answer"
        in answer
    )

    assert (
        "The expedition arrived"
        in answer
    )
