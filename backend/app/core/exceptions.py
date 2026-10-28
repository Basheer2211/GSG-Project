
class AppException(Exception):
    """Base exception for application errors."""
    pass


class EmailAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__("Email already registered")


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Invalid email or password")