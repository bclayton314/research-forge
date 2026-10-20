from io import BytesIO
from pathlib import Path


def test_upload_text_document(client, app):
    response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(b"ResearchForge test document."),
                "notes.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["original_filename"] == "notes.txt"
    assert data["status"] == "uploaded"
    assert data["content_type"] == "text/plain"
    assert data["size_bytes"] > 0

    assert data["filename"] != "notes.txt"
    assert data["filename"].endswith(".txt")

    upload_folder = Path(
        app.config["UPLOAD_FOLDER"]
    )

    saved_file = upload_folder / data["filename"]

    assert saved_file.exists()

    assert saved_file.read_bytes() == (
        b"ResearchForge test document."
    )


def test_upload_pdf_document(client, app):
    response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(b"%PDF-1.4 fake test content"),
                "research.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["original_filename"] == "research.pdf"
    assert data["filename"].endswith(".pdf")
    assert data["status"] == "uploaded"

    upload_folder = Path(
        app.config["UPLOAD_FOLDER"]
    )

    saved_file = upload_folder / data["filename"]

    assert saved_file.exists()


def test_upload_requires_file(client):
    response = client.post(
        "/api/documents/upload",
        data={},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "file is required",
    }


def test_upload_rejects_empty_filename(client):
    response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(b"test"),
                "",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": "filename is required",
    }


def test_upload_rejects_unsupported_file(client):
    response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(b"not allowed"),
                "malware.exe",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": (
            "unsupported file type; "
            "only PDF and TXT files are allowed"
        ),
    }