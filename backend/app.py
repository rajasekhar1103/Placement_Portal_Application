import os
import logging
from datetime import datetime

from flask import Flask, send_from_directory, send_file, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt, cache, mail, celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_celery(app):
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    celery.conf.timezone = "Asia/Kolkata"

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    # Resolve frontend path relative to this file
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    make_celery(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.company import company_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")

    # Serve uploaded files
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Serve frontend static assets (JS/CSS from /src/)
    @app.route("/src/<path:filename>")
    def serve_src(filename):
        src_dir = os.path.join(frontend_dir, "src")
        return send_from_directory(src_dir, filename)

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

    # Catch-all: serve index.html for all non-API routes
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return send_file(index_path)
        return jsonify({"error": "Frontend not found"}), 404

    with app.app_context():
        db.create_all()
        seed_admin(app)

    return app


def seed_admin(app):
    from models.models import User
    from config import Config

    existing = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not existing:
        admin = User(
            email=Config.ADMIN_EMAIL,
            role="admin",
            is_active=True,
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        logger.info(f"Admin user seeded: {Config.ADMIN_EMAIL}")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
