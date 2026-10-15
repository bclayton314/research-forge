from flask import Blueprint, jsonify, request

from .extensions import db
from .models import Document


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