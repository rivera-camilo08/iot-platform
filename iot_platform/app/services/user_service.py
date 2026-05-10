from uuid import UUID

from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_user(self, user_id: UUID) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def list_users(self) -> list[User]:
        return self.user_repository.list_all()
