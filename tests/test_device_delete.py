import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'iot_platform')))

from app.db.base import Base
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.repositories.device_repository import DeviceRepository


def setup_db(session):
    Base.metadata.create_all(bind=session.get_bind())


def test_delete_device_with_telemetry():
    session = SessionLocal()
    try:
        setup_db(session)
        user = User(name="User", email=f"u-{uuid4()}@test", password_hash="x", role=UserRole.user)
        session.add(user)
        session.commit()
        session.refresh(user)

        device = Device(name="D1", mac_address=f"m-{uuid4()}", device_token_hash="x", owner_id=user.id)
        session.add(device)
        session.commit()
        session.refresh(device)

        # add telemetry
        t = Telemetry(device_id=device.id, sensor_type="temp", value=1.23)
        session.add(t)
        session.commit()

        repo = DeviceRepository(session)
        # should delete telemetry and device without raising
        repo.delete(device)

        # assert device gone
        assert repo.get_by_id(device.id) is None
        # telemetry gone
        rem = session.query(Telemetry).filter(Telemetry.device_id == device.id).all()
        assert len(rem) == 0
    finally:
        session.rollback()
        session.close()
