from datetime import datetime
from typing import Any
from uuid import UUID

from app.models.telemetry import Telemetry
from app.repositories.telemetry_repository import TelemetryRepository


class TelemetryService:
    def __init__(self, telemetry_repository: TelemetryRepository) -> None:
        self.telemetry_repository = telemetry_repository

    def create_telemetry_records(self, device_id: UUID, payload: dict[str, Any]) -> list[Telemetry]:
        timestamp = payload.get("timestamp")
        recorded_at = None
        if timestamp:
            if isinstance(timestamp, str):
                recorded_at = datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, datetime):
                recorded_at = timestamp

        records: list[Telemetry] = []
        for sensor_type, value in payload.items():
            if sensor_type in {"device_token", "timestamp"}:
                continue
            try:
                reading = float(value)
            except (TypeError, ValueError):
                continue
            records.append(
                Telemetry(
                    device_id=device_id,
                    sensor_type=sensor_type,
                    value=reading,
                    recorded_at=recorded_at or datetime.utcnow(),
                )
            )
        if not records:
            raise ValueError("No se encontraron lecturas de sensores válidas")
        return self.telemetry_repository.create_many(records)

    def get_device_telemetry(self, device_id: UUID) -> list[Telemetry]:
        return self.telemetry_repository.get_by_device(device_id)

    def query_device_telemetry(
        self,
        device_id: UUID,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Telemetry]:
        return self.telemetry_repository.query_range(device_id, start=start, end=end)
