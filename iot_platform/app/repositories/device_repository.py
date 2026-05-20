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

    def list_all(self, skip: int = 0, limit: int = 50) -> list[Device]:
        query = self.session.query(Device).order_by(Device.created_at.desc())
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        return query.all()

    def list_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 50) -> list[Device]:
        query = self.session.query(Device).filter(Device.owner_id == owner_id).order_by(Device.created_at.desc())
        if skip:
            query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        return query.all()

    def create(self, device: Device) -> Device:
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def update(self, device: Device) -> Device:
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return device

    def delete(self, device: Device) -> None:
        self.session.delete(device)
        self.session.commit()
