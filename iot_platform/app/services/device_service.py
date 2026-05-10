import secrets
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

    def get_device_by_mac(self, mac_address: str) -> Device | None:
        return self.device_repository.get_by_mac(mac_address.lower())

    def list_devices(self, owner_id: UUID | None = None) -> list[Device]:
        if owner_id is None:
            return self.device_repository.list_all()
        return self.device_repository.list_by_owner(owner_id)

    @staticmethod
    def create_device_token() -> str:
        return secrets.token_urlsafe(32)

    def validate_device_auth(self, mac_address: str, device_token: str) -> Device | None:
        device = self.get_device_by_mac(mac_address)
        if not device or not verify_password(device_token, device.device_token_hash):
            return None
        if device.status != DeviceStatus.active:
            return None
        return device
