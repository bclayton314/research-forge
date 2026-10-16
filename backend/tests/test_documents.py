def test_create_document(client):
    response = client.post(
        "/api/documents",
        json={
            "filename": "test-document.pdf",
            "original_filename": "Test Document.pdf",
            "content_type": "application/pdf",
            "size_bytes": 12345,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["filename"] == "test-document.pdf"
    assert data["original_filename"] == "Test Document.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == 12345
    assert data["status"] == "pending"
    assert data["id"] is not None


def test_create_document_requires_filename(client):
    response = client.post(
        "/api/documents",
        json={
            "original_filename": "Test Document.pdf",
        },
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "filename is required",
    }


def test_create_document_requires_original_filename(client):
    response = client.post(
        "/api/documents",
        json={
            "filename": "test-document.pdf",
        },
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "original_filename is required",
    }


def test_list_documents(client):
    client.post(
        "/api/documents",
        json={
            "filename": "first.pdf",
            "original_filename": "First.pdf",
        },
    )

    client.post(
        "/api/documents",
        json={
            "filename": "second.pdf",
            "original_filename": "Second.pdf",
        },
    )

    response = client.get("/api/documents")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["documents"]) == 2


def test_get_document(client):
    create_response = client.post(
        "/api/documents",
        json={
            "filename": "test.pdf",
            "original_filename": "Test.pdf",
        },
    )

    document_id = create_response.get_json()["id"]

    response = client.get(
        f"/api/documents/{document_id}"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == document_id
    assert data["filename"] == "test.pdf"


def test_get_document_not_found(client):
    response = client.get(
        "/api/documents/"
        "11111111-1111-1111-1111-111111111111"
    )

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "document not found",
    }