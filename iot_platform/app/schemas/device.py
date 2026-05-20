from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    mac_address: str = Field(..., min_length=12, max_length=64)
    owner_id: UUID | None = None


class DeviceUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=120)
    status: str | None = None


class DeviceResponse(BaseModel):
    id: UUID
    name: str
    mac_address: str
    owner_id: UUID
    status: str
    created_at: datetime
    device_token: str | None = None

    model_config = {
        "from_attributes": True,
    }
