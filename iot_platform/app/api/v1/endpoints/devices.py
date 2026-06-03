from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_current_user, require_user_or_admin
from app.db.session import get_db
from app.models.device import Device, DeviceStatus
from app.models.user import UserRole
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse
from app.services.device_service import DeviceService
from app.core.security import generate_device_token
from app.utils.exceptions import EntityNotFound, UnauthorizedAction
from app.schemas.device import DeviceUpdate

router = APIRouter()


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    payload: DeviceCreate,
    current_user=Depends(require_user_or_admin),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device_token = generate_device_token()
    owner = current_user
    # Only superadmin may create devices for other users
    if payload.owner_id and current_user.role == UserRole.superadmin:
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
    resp = DeviceResponse.from_orm(device)
    # attach token only on creation response
    resp.device_token = device_token
    if current_user.role != UserRole.superadmin:
        resp.owner = None
    return resp


@router.get("/", response_model=list[DeviceResponse])
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeviceResponse]:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    # Only superadmin can list all devices
    if current_user.role == UserRole.superadmin:
        devices = service.list_devices(skip=skip, limit=limit)
    else:
        devices = service.list_devices_for_user(current_user, skip=skip, limit=limit)

    results: list[DeviceResponse] = []
    for device in devices:
        resp = DeviceResponse.from_orm(device)
        if current_user.role != UserRole.superadmin:
            resp.owner = None
        results.append(resp)
    return results


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: UUID = Path(..., description="ID del dispositivo"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device = service.get_device_by_id_for_user(device_id, current_user)
    if not device:
        raise EntityNotFound("Dispositivo no encontrado")
    # repository/service already filtered by user; additional check defensive
    if current_user.role not in {UserRole.superadmin, UserRole.admin} and device.owner_id != current_user.id:
        raise UnauthorizedAction()
    resp = DeviceResponse.from_orm(device)
    if current_user.role != UserRole.superadmin:
        resp.owner = None
    return resp


@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: UUID,
    payload: DeviceUpdate,
    current_user=Depends(require_user_or_admin),
    db: Session = Depends(get_db),
) -> DeviceResponse:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device = service.get_device_by_id_for_user(device_id, current_user)
    if not device:
        raise EntityNotFound("Dispositivo no encontrado")
    if current_user.role not in {UserRole.superadmin, UserRole.admin} and device.owner_id != current_user.id:
        raise UnauthorizedAction()

    # Convierte string → enum de forma segura
    status_value = None
    if payload.status is not None:
        try:
            status_value = DeviceStatus(payload.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado '{payload.status}' no válido. Valores permitidos: {[e.value for e in DeviceStatus]}"
            )

    # Valida que haya al menos un campo a actualizar
    if payload.name is None and payload.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar (name o status)"
        )

    try:
        updated = service.update_device(
            device_id=device_id,
            name=payload.name,
            status=status_value,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el dispositivo: {str(exc)}"
        )

    if not updated:
        raise EntityNotFound("Dispositivo no encontrado")
    resp = DeviceResponse.from_orm(updated)
    if current_user.role != UserRole.superadmin:
        resp.owner = None
    return resp


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: UUID,
    current_user=Depends(require_user_or_admin),
    db: Session = Depends(get_db),
) -> None:
    repository = DeviceRepository(db)
    service = DeviceService(repository)
    device = service.get_device_by_id_for_user(device_id, current_user)
    if not device:
        raise EntityNotFound("Dispositivo no encontrado")
    if current_user.role not in {UserRole.superadmin, UserRole.admin} and device.owner_id != current_user.id:
        raise UnauthorizedAction()
    service.delete_device(device_id)
    return None
