from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class TelemetryCreate(BaseModel):
    device_token: str = Field(..., min_length=8)
    timestamp: datetime | None = None
    sensor_type: str | None = None
    value: float | None = None


class TelemetryResponse(BaseModel):
    id: UUID
    device_id: UUID
    sensor_type: str
    value: float
    recorded_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TelemetryQuery(BaseModel):
    device_id: UUID | None = None
    from_timestamp: datetime | None = None
    to_timestamp: datetime | None = None
