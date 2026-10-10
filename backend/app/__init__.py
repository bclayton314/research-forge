import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .extensions import db, migrate


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def build_database_url():
    user = os.getenv("POSTGRES_USER", "research_forge")
    password = os.getenv("POSTGRES_PASSWORD", "research_forge_dev")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "research_forge")

    return (
        f"postgresql+psycopg://"
        f"{user}:{password}@{host}:{port}/{database}"
    )


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        JSON_SORT_KEYS=False,
        SQLALCHEMY_DATABASE_URI=build_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so SQLAlchemy and Alembic know about them.
    from . import models  # noqa: F401

    from .routes import api_bp

    app.register_blueprint(api_bp)

    return app