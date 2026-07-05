"""
Application-level exceptions.
"""


class AppException(Exception):
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)


class NotFoundException(AppException):
    status_code = 404
    message = "Resource not found"


class UnauthorizedException(AppException):
    status_code = 401
    message = "Unauthorized"


class ForbiddenException(AppException):
    status_code = 403
    message = "Forbidden"


class BadRequestException(AppException):
    status_code = 400
    message = "Bad request"


class ConflictException(AppException):
    status_code = 409
    message = "Resource already exists"


class LLMProviderException(AppException):
    """Raised when all LLM providers in the router fail."""
    status_code = 503
    message = "All LLM providers are currently unavailable"