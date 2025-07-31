from app.utils.exceptions.base import AppException


class DatabaseException(AppException):
    """Base error untuk database (Mongo, Redis, dll)."""

    def __init__(self, message="Database error", code=500):
        super().__init__(message, code)


class NotFoundError(DatabaseException):
    """Data tidak ditemukan di database."""

    def __init__(self, message="Data not found"):
        super().__init__(message, code=404)


class DuplicateKeyError(DatabaseException):
    """Duplicate key (misal insert unique field yg sudah ada)."""

    def __init__(self, message="Duplicate key error"):
        super().__init__(message, code=409)
