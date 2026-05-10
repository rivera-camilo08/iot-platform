from uuid import UUID
from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    mac_address: str = Field(..., min_length=12, max_length=64)
    owner_id: UUID | None = None


class DeviceResponse(BaseModel):
    id: UUID
    name: str
    mac_address: str
    owner_id: UUID
    status: str
    created_at: str
    device_token: str | None = None

    model_config = {
        "from_attributes": True,
    }
