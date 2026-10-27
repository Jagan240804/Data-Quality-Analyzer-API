import os
from flask import Flask, jsonify, render_template
from .models import db


def create_app(config=None):
    """Application factory. Uses SQLite by default; set DATABASE_URL for PostgreSQL."""
    app = Flask(__name__)
    db_url = os.environ.get("DATABASE_URL", "sqlite:///dq.db")
    if db_url.startswith("postgres://"):  # SQLAlchemy needs postgresql://
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=db_url,
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5 MB upload limit
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    from .routes import api
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.errorhandler(413)
    def too_large(_):
        return jsonify(error="File too large (max 5 MB)"), 413

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="Not found"), 404

    with app.app_context():
        db.create_all()
    return app
