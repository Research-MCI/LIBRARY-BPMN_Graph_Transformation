import os

from dotenv import load_dotenv

ENV_PATH = os.getenv("ENV_PATH", ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)


class Config:
    """Base config (default for production)"""

    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/your_db")
    DB_NAME = os.getenv("DB_NAME", "your_db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR = os.getenv("LOG_DIR", "logs")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    TESTING = False
    GUNICORN_WORKERS = int(os.getenv("GUNICORN_WORKERS", 4))


class DevelopmentConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True


class TestingConfig(Config):
    FLASK_ENV = "testing"
    TESTING = True
    DEBUG = True
    MONGO_URI = os.getenv("MONGO_URI_TEST", "mongodb://localhost:27017/test_db")


class StagingConfig(Config):
    FLASK_ENV = "staging"
    DEBUG = False


class ProductionConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False


def get_config():
    env = os.getenv("FLASK_ENV", "production").lower()
    if env == "development":
        return DevelopmentConfig
    elif env == "testing":
        return TestingConfig
    elif env == "staging":
        return StagingConfig
    else:
        return ProductionConfig
