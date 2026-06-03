from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.device import Device
from app.models.user import UserRole
from app.repositories.device_repository import DeviceRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry import TelemetryResponse
from app.services.telemetry_service import TelemetryService

router = APIRouter()


@router.get("/devices/{device_id}/telemetry", response_model=list[TelemetryResponse])
def get_device_telemetry(
    device_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    if current_user.role != UserRole.admin and device.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    telemetry = TelemetryService(TelemetryRepository(db)).get_device_telemetry(
        device_id,
        skip=skip,
        limit=limit,
    )
    return [TelemetryResponse.from_orm(record) for record in telemetry]


@router.get("/telemetry", response_model=list[TelemetryResponse])
def query_telemetry(
    device_id: UUID | None = Query(None),
    from_timestamp: datetime | None = Query(None, alias="from"),
    to_timestamp: datetime | None = Query(None, alias="to"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TelemetryResponse]:
    if not device_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="device_id es obligatorio")
    device = DeviceRepository(db).get_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    if current_user.role != UserRole.admin and device.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    telemetry = TelemetryService(TelemetryRepository(db)).query_device_telemetry(
        device_id=device_id,
        start=from_timestamp,
        end=to_timestamp,
        skip=skip,
        limit=limit,
    )
    return [TelemetryResponse.from_orm(record) for record in telemetry]
