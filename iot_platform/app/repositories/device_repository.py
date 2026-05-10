from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.device import Device


class DeviceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        return self.session.query(Device).filter(Device.id == device_id).one_or_none()

    def get_by_mac(self, mac_address: str) -> Optional[Device]:
        return self.session.query(Device).filter(Device.mac_address == mac_address).one_or_none()

    def list_all(self) -> list[Device]:
        return self.session.query(Device).order_by(Device.created_at.desc()).all()

    def list_by_owner(self, owner_id: UUID) -> list[Device]:
        return self.session.query(Device).filter(Device.owner_id == owner_id).order_by(Device.created_at.desc()).all()

    def create(self, device: Device) -> Device:
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device
