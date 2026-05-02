import logging
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_mail import Mail
from flask_cors import CORS
from celery import Celery

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()
mail = Mail()
cors = CORS()
celery = Celery()


def setup_logging(app):
    """Setup logging for the Flask app."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    # Reduce noise from libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    app.logger.info("Logging setup complete.")
