class ApplicationException(Exception):
    """Base exception for application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ValidationException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 422)


class LlamaCloudException(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 500)


class NotFound(ApplicationException):
    def __init__(self, message: str):
        super().__init__(message, 404)
