from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from .extensions import db
from .extraction import ExtractionError, extract_text
from .models import Document, DocumentChunk
from .storage import is_allowed_file, save_uploaded_file
from .chunking import chunk_text
from .search import make_snippet, parse_query, score_text
from .embeddings import embed_texts
from sqlalchemy import or_
from io import BytesIO


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "research-forge-api",
        }
    )


@api_bp.post("/documents")
def create_document():
    data = request.get_json(silent=True) or {}

    filename = data.get("filename")
    original_filename = data.get("original_filename")

    if not filename:
        return jsonify(
            {
                "error": "filename is required",
            }
        ), 400

    if not original_filename:
        return jsonify(
            {
                "error": "original_filename is required",
            }
        ), 400

    document = Document(
        filename=filename,
        original_filename=original_filename,
        content_type=data.get("content_type"),
        size_bytes=data.get("size_bytes"),
        storage_key=data.get("storage_key"),
        status=data.get("status", "pending"),
    )

    db.session.add(document)
    db.session.commit()

    return jsonify(document.to_dict()), 201


@api_bp.post("/documents/upload")
def upload_document():
    if "file" not in request.files:
        return jsonify(
            {
                "error": "file is required",
            }
        ), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify(
            {
                "error": "filename is required",
            }
        ), 400

    if not is_allowed_file(file.filename):
        return jsonify(
            {
                "error": (
                    "unsupported file type; "
                    "only PDF and TXT files are allowed"
                ),
            }
        ), 400

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    )

    storage_filename, saved_path = save_uploaded_file(
        file,
        upload_folder,
    )

    document = Document(
        filename=storage_filename,
        original_filename=file.filename,
        content_type=file.content_type,
        size_bytes=saved_path.stat().st_size,
        storage_key=storage_filename,
        status="uploaded",
    )

    db.session.add(document)
    db.session.commit()

    return jsonify(document.to_dict()), 201


@api_bp.get("/documents")
def list_documents():
    documents = (
        db.session.execute(
            db.select(Document).order_by(
                Document.created_at.desc()
            )
        )
        .scalars()
        .all()
    )

    return jsonify(
        {
            "documents": [
                document.to_dict()
                for document in documents
            ]
        }
    )


@api_bp.get("/documents/<uuid:document_id>")
def get_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        return jsonify(
            {
                "error": "document not found",
            }
        ), 404

    return jsonify(document.to_dict())


@api_bp.post("/documents/<uuid:document_id>/process")
def process_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        return jsonify(
            {
                "error": "document not found",
            }
        ), 404

    if not document.storage_key:
        return jsonify(
            {
                "error": "document has no stored file",
            }
        ), 400

    upload_folder = Path(
        current_app.config["UPLOAD_FOLDER"]
    )

    file_path = upload_folder / document.storage_key

    if not file_path.exists():
        return jsonify(
            {
                "error": "stored file not found",
            }
        ), 404

    try:
        document.status = "processing"
        db.session.commit()

        extracted_text = extract_text(file_path)

        document.extracted_text = extracted_text
        document.status = "processed"

        db.session.commit()

        return jsonify(document.to_dict())

    except ExtractionError as exc:
        document.status = "failed"
        db.session.commit()

        return jsonify(
            {
                "error": str(exc),
            }
        ), 422


@api_bp.post("/documents/<uuid:document_id>/chunk")
def chunk_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        return jsonify(
            {
                "error": "document not found",
            }
        ), 404

    if document.status != "processed":
        return jsonify(
            {
                "error": (
                    "document must be processed "
                    "before chunking"
                ),
            }
        ), 400

    if document.extracted_text is None:
        return jsonify(
            {
                "error": "document has no extracted text",
            }
        ), 400

    chunks = chunk_text(
        document.extracted_text,
    )

    db.session.execute(
        db.delete(DocumentChunk).where(
            DocumentChunk.document_id
            == document.id
        )
    )

    for index, text in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            text=text,
            character_count=len(text),
        )

        db.session.add(chunk)

    document.status = "chunked"

    db.session.commit()

    return jsonify(
        {
            "document_id": str(document.id),
            "status": document.status,
            "chunk_count": len(chunks),
        }
    )


@api_bp.get("/documents/<uuid:document_id>/chunks")
def list_document_chunks(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        return jsonify(
            {
                "error": "document not found",
            }
        ), 404

    chunks = (
        db.session.execute(
            db.select(DocumentChunk)
            .where(
                DocumentChunk.document_id
                == document.id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
        )
        .scalars()
        .all()
    )

    return jsonify(
        {
            "document_id": str(document.id),
            "chunks": [
                chunk.to_dict()
                for chunk in chunks
            ],
        }
    )


@api_bp.get("/search")
def search_documents():
    query = request.args.get(
        "q",
        "",
    ).strip()

    if not query:
        return jsonify(
            {
                "error": "q query parameter is required",
            }
        ), 400

    try:
        limit = int(
            request.args.get(
                "limit",
                10,
            )
        )
    except ValueError:
        return jsonify(
            {
                "error": "limit must be an integer",
            }
        ), 400

    limit = max(
        1,
        min(limit, 50),
    )

    terms = parse_query(query)

    if not terms:
        return jsonify(
            {
                "query": query,
                "results": [],
            }
        )

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
                "document_name": (
                    document.original_filename
                ),
                "chunk_id": str(
                    chunk.id
                ),
                "chunk_index": (
                    chunk.chunk_index
                ),
                "score": score,
                "snippet": make_snippet(
                    chunk.text,
                    terms,
                ),
            }
        )

    results.sort(
        key=lambda result: result["score"],
        reverse=True,
    )

    return jsonify(
        {
            "query": query,
            "result_count": min(
                len(results),
                limit,
            ),
            "results": results[:limit],
        }
    )


def create_searchable_document(client):
    text = (
        "The Boxer Rebellion occurred in China. "
        "Foreign influence in China contributed "
        "to considerable political unrest. "
        "The Boxer movement opposed foreign "
        "intervention."
    )

    upload_response = client.post(
        "/api/documents/upload",
        data={
            "file": (
                BytesIO(
                    text.encode("utf-8")
                ),
                "history.txt",
            ),
        },
        content_type="multipart/form-data",
    )

    assert upload_response.status_code == 201

    document_id = (
        upload_response
        .get_json()["id"]
    )

    process_response = client.post(
        f"/api/documents/{document_id}/process"
    )

    assert process_response.status_code == 200

    chunk_response = client.post(
        f"/api/documents/{document_id}/chunk"
    )

    assert chunk_response.status_code == 200

    return document_id


def test_search_documents(client):
    document_id = create_searchable_document(
        client
    )

    response = client.get(
        "/api/search?q=boxer"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["query"] == "boxer"
    assert data["result_count"] >= 1

    result = data["results"][0]

    assert result["document_id"] == document_id
    assert result["document_name"] == "history.txt"
    assert result["score"] >= 1
    assert "Boxer" in result["snippet"]


def test_search_multiple_terms(client):
    create_searchable_document(
        client
    )

    response = client.get(
        "/api/search?q=china+boxer"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["result_count"] >= 1

    assert (
        data["results"][0]["score"]
        >= 2
    )


def test_search_requires_query(client):
    response = client.get(
        "/api/search"
    )

    assert response.status_code == 400

    assert response.get_json() == {
        "error": (
            "q query parameter is required"
        ),
    }


def test_search_returns_empty_results(
    client,
):
    create_searchable_document(
        client
    )

    response = client.get(
        "/api/search?q=quantummechanics"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["result_count"] == 0
    assert data["results"] == []


@api_bp.post("/documents/<uuid:document_id>/embed")
def embed_document(document_id):
    document = db.session.get(
        Document,
        document_id,
    )

    if document is None:
        return jsonify(
            {
                "error": "document not found",
            }
        ), 404

    chunks = (
        db.session.execute(
            db.select(DocumentChunk)
            .where(
                DocumentChunk.document_id
                == document.id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
        )
        .scalars()
        .all()
    )

    if not chunks:
        return jsonify(
            {
                "error": (
                    "document must be chunked "
                    "before embedding"
                ),
            }
        ), 400

    texts = [
        chunk.text
        for chunk in chunks
    ]

    embeddings = embed_texts(texts)

    for chunk, embedding in zip(
        chunks,
        embeddings,
        strict=True,
    ):
        chunk.embedding = embedding

    document.status = "embedded"

    db.session.commit()

    return jsonify(
        {
            "document_id": str(document.id),
            "status": document.status,
            "embedded_chunk_count": len(chunks),
        }
    )
