from datetime import datetime
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry


class TelemetryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_many(self, telemetry_batch: Iterable[Telemetry]) -> list[Telemetry]:
        self.session.add_all(telemetry_batch)
        self.session.commit()
        for record in telemetry_batch:
            self.session.refresh(record)
        return list(telemetry_batch)

    def get_by_device(self, device_id: UUID) -> list[Telemetry]:
        return (
            self.session.query(Telemetry)
            .filter(Telemetry.device_id == device_id)
            .order_by(Telemetry.recorded_at.desc())
            .all()
        )

    def query_range(self, device_id: UUID, start: datetime | None = None, end: datetime | None = None) -> list[Telemetry]:
        query = self.session.query(Telemetry).filter(Telemetry.device_id == device_id)
        if start:
            query = query.filter(Telemetry.recorded_at >= start)
        if end:
            query = query.filter(Telemetry.recorded_at <= end)
        return query.order_by(Telemetry.recorded_at.desc()).all()
