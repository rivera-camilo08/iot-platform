import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "iot_platform")))

from app.db.base import Base
from app.db.session import SessionLocal
from app.models.device import Device
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


def test_has_devices_returns_true_for_user_with_assigned_devices():
    session = SessionLocal()
    try:
        Base.metadata.create_all(bind=session.get_bind())
        user = User(
            name="Test User",
            email=f"user-{uuid4()}@example.com",
            password_hash="hash",
            role=UserRole.user,
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        device = Device(
            name="Test Device",
            mac_address=f"mac-{uuid4()}",
            device_token_hash="hash",
            owner_id=user.id,
        )
        session.add(device)
        session.commit()

        repo = UserRepository(session)
        assert repo.has_devices(user.id) is True
    finally:
        session.rollback()
        session.close()
