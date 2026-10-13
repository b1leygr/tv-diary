from app.core.exceptions import DomainException


class AuthServiceError(DomainException):
    pass


class AuthenticationError(AuthServiceError):
    def __init__(self, message: str = "Incorrect username or password"):
        super().__init__(title="Authentication Error", status_code=401, message=message)


class InvalidCredentials(AuthServiceError):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(title="Invalid Credentials", status_code=401, message=message)
