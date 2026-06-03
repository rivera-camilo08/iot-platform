import os
import sys
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "iot_platform")))

from app.db.base import Base
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from app.services.device_service import DeviceService


def setup_db(session):
    Base.metadata.create_all(bind=session.get_bind())


def test_list_for_user_and_superadmin():
    session = SessionLocal()
    try:
        setup_db(session)
        # create users
        user1 = User(name="User1", email=f"u1-{uuid4()}@test", password_hash="x", role=UserRole.user)
        user2 = User(name="User2", email=f"u2-{uuid4()}@test", password_hash="x", role=UserRole.user)
        superadmin = User(name="Admin", email=f"adm-{uuid4()}@test", password_hash="x", role=UserRole.superadmin)
        session.add_all([user1, user2, superadmin])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        session.refresh(superadmin)

        # create devices
        d1 = Device(name="D1", mac_address=f"m1-{uuid4()}", device_token_hash="x", owner_id=user1.id)
        d2 = Device(name="D2", mac_address=f"m2-{uuid4()}", device_token_hash="x", owner_id=user2.id)
        session.add_all([d1, d2])
        session.commit()

        repo = DeviceRepository(session)
        svc = DeviceService(repo)

        # user1 should see only their device
        devices_user1 = repo.list_for_user(user1)
        assert len(devices_user1) == 1
        assert devices_user1[0].owner_id == user1.id

        # superadmin should see both
        devices_admin = repo.list_for_user(superadmin)
        assert len(devices_admin) >= 2

        # service wrapper
        devices_user1_svc = svc.list_devices_for_user(user1)
        assert len(devices_user1_svc) == 1

    finally:
        session.rollback()
        session.close()


def test_get_by_id_for_user():
    session = SessionLocal()
    try:
        setup_db(session)
        user1 = User(name="User1", email=f"u1-{uuid4()}@test", password_hash="x", role=UserRole.user)
        user2 = User(name="User2", email=f"u2-{uuid4()}@test", password_hash="x", role=UserRole.user)
        superadmin = User(name="Admin", email=f"adm-{uuid4()}@test", password_hash="x", role=UserRole.superadmin)
        session.add_all([user1, user2, superadmin])
        session.commit()
        session.refresh(user1)
        session.refresh(user2)
        session.refresh(superadmin)

        d1 = Device(name="D1", mac_address=f"m1-{uuid4()}", device_token_hash="x", owner_id=user1.id)
        session.add(d1)
        session.commit()
        session.refresh(d1)

        repo = DeviceRepository(session)

        # user2 should not get device d1
        assert repo.get_by_id_for_user(d1.id, user2) is None

        # owner should get it
        assert repo.get_by_id_for_user(d1.id, user1) is not None

        # superadmin should get it
        assert repo.get_by_id_for_user(d1.id, superadmin) is not None

    finally:
        session.rollback()
        session.close()


def test_admin_can_access_other_users_device():
    session = SessionLocal()
    try:
        setup_db(session)
        owner = User(name="Owner", email=f"owner-{uuid4()}@test", password_hash="x", role=UserRole.user)
        admin = User(name="Admin", email=f"admin-{uuid4()}@test", password_hash="x", role=UserRole.admin)
        session.add_all([owner, admin])
        session.commit()
        session.refresh(owner)
        session.refresh(admin)

        device = Device(name="D1", mac_address=f"m1-{uuid4()}", device_token_hash="x", owner_id=owner.id)
        session.add(device)
        session.commit()
        session.refresh(device)

        repo = DeviceRepository(session)
        svc = DeviceService(repo)

        assert repo.get_by_id_for_user(device.id, admin) is not None
        assert svc.get_device_by_id_for_user(device.id, admin) is not None
        assert len(repo.list_for_user(admin)) == 1
    finally:
        session.rollback()
        session.close()
