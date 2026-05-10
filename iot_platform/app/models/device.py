import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DeviceStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    mac_address: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    device_token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[DeviceStatus] = mapped_column(Enum(DeviceStatus), default=DeviceStatus.active, nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="devices", lazy="joined")
    telemetry: Mapped[list["Telemetry"]] = relationship("Telemetry", back_populates="device", lazy="selectin")
