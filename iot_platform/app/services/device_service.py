from uuid import UUID

from app.core.security import hash_password, verify_password
from app.models.device import Device, DeviceStatus
from app.models.user import User
from app.repositories.device_repository import DeviceRepository


class DeviceService:
    def __init__(self, device_repository: DeviceRepository) -> None:
        self.device_repository = device_repository

    def create_device(self, name: str, mac_address: str, device_token: str, owner: User) -> Device:
        if self.device_repository.get_by_mac(mac_address):
            raise ValueError("La dirección MAC ya está registrada")

        device = Device(
            name=name,
            mac_address=mac_address.lower(),
            device_token_hash=hash_password(device_token),
            owner_id=owner.id,
            status=DeviceStatus.active,
        )
        return self.device_repository.create(device)

    def get_device_by_id(self, device_id: UUID) -> Device | None:
        return self.device_repository.get_by_id(device_id)

    def get_device_by_id_for_user(self, device_id: UUID, user) -> Device | None:
        return self.device_repository.get_by_id_for_user(device_id, user)

    def get_device_by_mac(self, mac_address: str) -> Device | None:
        return self.device_repository.get_by_mac(mac_address.lower())

    def list_devices(self, owner_id: UUID | None = None, skip: int = 0, limit: int = 50) -> list[Device]:
        if owner_id is None:
            return self.device_repository.list_all(skip=skip, limit=limit)
        return self.device_repository.list_by_owner(owner_id, skip=skip, limit=limit)

    def list_devices_for_user(self, user, skip: int = 0, limit: int = 50) -> list[Device]:
        return self.device_repository.list_for_user(user, skip=skip, limit=limit)

    # device token generation moved to app.core.security.generate_device_token

    def validate_device_auth(self, mac_address: str, device_token: str) -> Device | None:
        device = self.get_device_by_mac(mac_address)
        if not device or not verify_password(device_token, device.device_token_hash):
            return None
        if device.status != DeviceStatus.active:
            return None
        return device

    def update_device(self, device_id: UUID, name: str | None = None, status: DeviceStatus | None = None) -> Device | None:
        device = self.get_device_by_id(device_id)
        if not device:
            return None
        if name is not None:
            device.name = name
        if status is not None:
            device.status = status
        return self.device_repository.update(device)

    def delete_device(self, device_id: UUID) -> bool:
        device = self.get_device_by_id(device_id)
        if not device:
            return False
        self.device_repository.delete(device)
        return True
