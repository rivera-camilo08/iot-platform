from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).one_or_none()

    def list_all(self) -> list[User]:
        return self.session.query(User).order_by(User.created_at.desc()).all()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
