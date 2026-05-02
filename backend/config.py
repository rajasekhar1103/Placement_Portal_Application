import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _redis_available(url):
    """Check if Redis is reachable."""
    try:
        import redis
        client = redis.from_url(url, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ppa-super-secret-key-2024")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ppa-jwt-secret-2024")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds

    # SQLite
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "ppa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Flask-Caching – auto-detects Redis, falls back to SimpleCache
    _REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    if _redis_available(_REDIS_URL):
        CACHE_TYPE = "RedisCache"
        CACHE_REDIS_URL = _REDIS_URL
    else:
        CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery (optional – only needed when Celery workers are running)
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")


    # Mail (using a dummy SMTP for dev – replace with real SMTP for production)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "ppa@placement.edu")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "ppa_dev.db"))


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/ppa_prod")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

    # Admin default credentials (seeded on first run)
    ADMIN_EMAIL = "admin@ppa.com"
    ADMIN_PASSWORD = "admin123"
    ADMIN_NAME = "Institute Admin"

    # Upload folder for resumes
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    # Frontend URL for CORS
    FRONTEND_URL = "http://localhost:8080"
