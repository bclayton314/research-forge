from io import BytesIO


def test_process_text_document(client):
    upload_response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(
                    b"ResearchForge extracted text test."
                ),
                "notes.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    assert upload_response.status_code == 201

    document_id = upload_response.get_json()["id"]

    response = client.post(
        f"/api/documents/{document_id}/process"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "processed"
    assert (
        data["extracted_text"]
        == "ResearchForge extracted text test."
    )


def test_process_document_not_found(client):
    response = client.post(
        "/api/documents/"
        "11111111-1111-1111-1111-111111111111"
        "/process"
    )

    assert response.status_code == 404

    assert response.get_json() == {
        "error": "document not found",
    }


def test_process_document_without_stored_file(client):
    create_response = client.post(
        "/api/documents",
        json={
            "filename": "metadata-only.txt",
            "original_filename": "metadata-only.txt",
        },
    )

    document_id = create_response.get_json()["id"]

    response = client.post(
        f"/api/documents/{document_id}/process"
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "document has no stored file",
    }


