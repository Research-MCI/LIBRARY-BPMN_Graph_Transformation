import os

from pymongo import MongoClient, errors

from app.infrastructure.config import get_config
from app.utils.exceptions.db_exceptions import DatabaseException
from app.utils.logger import get_logger

logger = get_logger(__name__)
_config = get_config()


class MongoDB:
    """
    MongoDB Client wrapper for dependency injection, testability, and clean usage.
    """

    def __init__(self, uri=None, db_name=None, client_class=MongoClient):
        self.uri = uri or _config.MONGO_URI

        self.db_name = (
            db_name
            or self._get_db_name_from_config()
        )
        self.client_class = client_class
        self.client = None
        self.db = None

    def connect(self):
        if self.client is not None and self.db is not None:
            return
        try:
            self.client = self.client_class(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            # Hide credentials in log (show only after @ if exists)
            safe_uri = self.uri
            if "@" in safe_uri:
                safe_uri = safe_uri.rsplit("@", 1)[-1]
            logger.info(
                f"Connected to MongoDB at {safe_uri}, using DB '{self.db_name}'"
            )
        except errors.ConnectionFailure as e:
            logger.error(f"MongoDB connection failed (ConnectionFailure): {e}")
            raise DatabaseException(
                "MongoDB connection failed: Unable to connect to server"
            )
        except errors.PyMongoError as e:
            logger.error(f"MongoDB error: {e}")
            raise DatabaseException(f"MongoDB error: {e}")

    def get_db(self):
        if self.db is None:
            self.connect()
        return self.db

    def get_collection(self, name):
        db = self.get_db()
        return db[name]

    @staticmethod
    def _extract_db_name(uri):
        # Extract the db name from a standard MongoDB URI, safe for both "mongodb://host/db" and with params
        try:
            db_name = uri.rsplit("/", 1)[-1]
            if "?" in db_name:
                db_name = db_name.split("?", 1)[0]
            return db_name
        except Exception:
            return None

    @staticmethod
    def _get_db_name_from_config():
        return getattr(_config, "DB_NAME", os.getenv("DB_NAME", "your_db"))


# Singleton instance for main app usage
mongo = MongoDB()


def get_db():
    """Get main database instance (singleton)."""
    return mongo.get_db()


def get_collection(name):
    """Get a collection with a specific name from main db (singleton)."""
    return mongo.get_collection(name)
