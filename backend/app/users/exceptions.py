from fastapi import status

from app.core.exceptions import DomainException


class ExistingUser(DomainException):
    def __init__(self, username: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, message=f"User with username '{username}' already exists.")

class UserNotFound(DomainException):
    def __init__(self, user_id: int | None = None, username: str | None = None):
       self.user = str(user_id) if user_id is not None else username
       super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=f"User '{self.user}' not found." if self.user else "No users found.")
