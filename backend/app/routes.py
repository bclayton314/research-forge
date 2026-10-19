from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from .extensions import db
from .models import Document
from .storage import is_allowed_file, save_uploaded_file


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