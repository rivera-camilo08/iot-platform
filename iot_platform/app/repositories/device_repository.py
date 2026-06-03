from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.user import UserRole
from app.models.telemetry import Telemetry


class DeviceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, device_id: UUID) -> Optional[Device]:
        return self.session.query(Device).filter(Device.id == device_id).one_or_none()

    def get_by_id_for_user(self, device_id: UUID, user) -> Optional[Device]:
        """Return device if `user` is authorized to see it.

        Superadmins and admins see any device. Normal users only see their own devices.
        """
        query = self.session.query(Device).filter(Device.id == device_id)
        if getattr(user, "role", None) not in {UserRole.superadmin, UserRole.admin}:
            query = query.filter(Device.owner_id == user.id)
        return query.one_or_none()

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

    def list_for_user(self, user, skip: int = 0, limit: int = 50) -> list[Device]:
        """List devices depending on user permissions.

        Superadmins and admins see all devices; normal users see only their own.
        """
        if getattr(user, "role", None) in {UserRole.superadmin, UserRole.admin}:
            return self.list_all(skip=skip, limit=limit)
        return self.list_by_owner(user.id, skip=skip, limit=limit)

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
        # Remove telemetry rows first to avoid FK constraint errors on some DBs
        try:
            telemetry_rows = self.session.query(Telemetry).filter(Telemetry.device_id == device.id).all()
            for row in telemetry_rows:
                self.session.delete(row)
        except Exception:
            # best effort; if DB handles cascade, continue
            pass
        self.session.delete(device)
        self.session.commit()
