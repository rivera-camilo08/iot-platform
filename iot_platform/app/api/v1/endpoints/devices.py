from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_user, require_user_or_admin
from app.db.session import get_db
from app.models.device import Device
from app.models.user import UserRole
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.device_service import DeviceService

router = APIRouter()


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    current_user=Depends(require_user_or_admin),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device_token = service.create_device_token()
    owner = current_user
    if current_user.role == UserRole.admin and payload.owner_id:
        from app.repositories.user_repository import UserRepository

        owner = UserRepository(db).get_by_id(payload.owner_id) or current_user

    try:
        device = service.create_device(
            name=payload.name,
            mac_address=payload.mac_address,
            device_token=device_token,
            owner=owner,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return DeviceResponse(
        id=device.id,
        name=device.name,
        mac_address=device.mac_address,
        owner_id=device.owner_id,
        status=device.status.value,
        created_at=device.created_at.isoformat(),
        device_token=device_token,
    )


@router.get("/", response_model=list[DeviceResponse])
def list_devices(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeviceResponse]:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    if current_user.role == UserRole.admin:
        devices = service.list_devices()
    else:
        devices = service.list_devices(owner_id=current_user.id)
    return [DeviceResponse.from_orm(device) for device in devices]


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: UUID = Path(..., description="ID del dispositivo"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device = service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    if current_user.role != UserRole.admin and device.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return DeviceResponse.from_orm(device)
