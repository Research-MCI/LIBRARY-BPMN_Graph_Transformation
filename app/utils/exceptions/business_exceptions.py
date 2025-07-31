from app.utils.exceptions.base import AppException


class BusinessException(AppException):
    """Untuk error business logic (misal validasi, rule bisnis)."""

    def __init__(self, message="Business logic error", code=400):
        super().__init__(message, code)


class ValidationError(BusinessException):
    """Error validasi data input user."""

    def __init__(self, message="Validation failed"):
        super().__init__(message, code=422)


class ConflictError(BusinessException):
    """Error data bentrok (misal sudah ada, duplikasi)."""

    def __init__(self, message="Resource conflict"):
        super().__init__(message, code=409)
