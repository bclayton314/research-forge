from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        JSON_SORT_KEYS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    CORS(app)

    from .routes import api_bp

    app.register_blueprint(api_bp)

    return app