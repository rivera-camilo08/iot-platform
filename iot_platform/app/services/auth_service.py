import secrets
from datetime import timedelta
from uuid import UUID

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register_user(self, name: str, email: str, password: str) -> User:
        if self.user_repository.get_by_email(email):
            raise ValueError("El correo ya está registrado")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.user,
            is_active=True,
        )
        return self.user_repository.create(user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_tokens(self, subject: UUID) -> Token:
        access_token = create_access_token(str(subject), expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(str(subject), expires_delta=timedelta(days=30))
        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_token(self, user_id: UUID) -> Token:
        return self.create_tokens(user_id)

    @staticmethod
    def create_device_token() -> str:
        return secrets.token_urlsafe(32)
