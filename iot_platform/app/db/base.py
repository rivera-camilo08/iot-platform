from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:  # pragma: no cover
        return cls.__name__.lower()

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
