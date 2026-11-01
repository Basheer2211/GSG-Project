
class AppException(Exception):
    """Base exception for application errors."""
    pass


class EmailAlreadyExistsError(AppException):
    def __init__(self, message: str = "Email already registered"):
        super().__init__(message)


class InvalidCredentialsError(AppException):
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message)