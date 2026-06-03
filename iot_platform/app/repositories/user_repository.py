from typing import Optional
from uuid import UUID

from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).one_or_none()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return (
            self.session.query(User)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def has_devices(self, user_id: UUID) -> bool:
        return self.session.query(exists().where(Device.owner_id == user_id)).scalar()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
