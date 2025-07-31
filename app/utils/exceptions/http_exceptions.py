from app.utils.exceptions.base import AppException


class HTTPException(AppException):
    """Untuk custom HTTP error response."""

    def __init__(self, message="HTTP error", code=400):
        super().__init__(message, code)


class UnauthorizedError(HTTPException):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, code=401)


class ForbiddenError(HTTPException):
    def __init__(self, message="Forbidden"):
        super().__init__(message, code=403)


class BadRequestError(HTTPException):
    def __init__(self, message="Bad request"):
        super().__init__(message, code=400)


class TooManyRequestsError(HTTPException):
    def __init__(self, message="Too many requests"):
        super().__init__(message, code=429)
