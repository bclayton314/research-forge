from io import BytesIO

from app.chunking import chunk_text


def test_chunk_text_splits_long_text():
    text = "A" * 2500

    chunks = chunk_text(
        text,
        chunk_size=1000,
        overlap=100,
    )

    assert len(chunks) == 3

    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    assert len(chunks[2]) == 700


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []


def test_chunk_text_rejects_invalid_overlap():
    try:
        chunk_text(
            "test",
            chunk_size=100,
            overlap=100,
        )
    except ValueError as exc:
        assert str(exc) == (
            "overlap must be smaller than chunk_size"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_chunk_processed_document(client):
    text = (
        "ResearchForge test content. "
        * 100
    )

    upload_response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(
                    text.encode("utf-8")
                ),
                "research.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    assert upload_response.status_code == 201

    document_id = upload_response.get_json()["id"]

    process_response = client.post(
        f"/api/documents/{document_id}/process"
    )

    assert process_response.status_code == 200

    chunk_response = client.post(
        f"/api/documents/{document_id}/chunk"
    )

    assert chunk_response.status_code == 200

    data = chunk_response.get_json()

    assert data["status"] == "chunked"
    assert data["chunk_count"] > 1

    chunks_response = client.get(
        f"/api/documents/{document_id}/chunks"
    )

    assert chunks_response.status_code == 200

    chunks_data = chunks_response.get_json()

    assert (
        len(chunks_data["chunks"])
        == data["chunk_count"]
    )

    assert (
        chunks_data["chunks"][0]["chunk_index"]
        == 0
    )


def test_chunk_document_requires_processing(client):
    upload_response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(b"Unprocessed document."),
                "notes.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    document_id = upload_response.get_json()["id"]

    response = client.post(
        f"/api/documents/{document_id}/chunk"
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": (
            "document must be processed "
            "before chunking"
        ),
    }


def test_chunk_document_not_found(client):
    response = client.post(
        "/api/documents/"
        "11111111-1111-1111-1111-111111111111"
        "/chunk"
    )

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "document not found",
    }