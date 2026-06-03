from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.device import DeviceStatus


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    mac_address: str = Field(..., min_length=12, max_length=64)
    owner_id: UUID | None = None


class DeviceUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=120)
    status: str | None = None

    @field_validator("status")
    @classmethod
    def status_debe_ser_valido(cls, v: str | None) -> str | None:
        if v is None:
            return v
        valores_validos = [e.value for e in DeviceStatus]
        if v not in valores_validos:
            raise ValueError(
                f"Estado '{v}' no válido. Valores permitidos: {valores_validos}"
            )
        return v


class DeviceResponse(BaseModel):
    id: UUID
    name: str
    mac_address: str
    owner_id: UUID
    owner: Optional["OwnerResponse"] = None
    status: str
    created_at: datetime
    device_token: str | None = None

    model_config = {
        "from_attributes": True,
    }


class OwnerResponse(BaseModel):
    id: UUID
    name: str
    email: str

    model_config = {"from_attributes": True}
