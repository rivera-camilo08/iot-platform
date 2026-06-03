import os
import sys
from pathlib import Path

from pydantic import ValidationError

cwd = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'iot_platform')))

from app.schemas.device import DeviceUpdate


def test_device_update_status_validates_enum():
    valid = DeviceUpdate(name="Sensor", status="active")
    assert valid.status.name == "active"


def test_device_update_rejects_invalid_status():
    try:
        DeviceUpdate(name="Sensor", status="unknown")
        assert False, "Expected ValidationError for invalid status"
    except ValidationError as exc:
        assert "status" in str(exc)
        assert "Input should be 'active' or 'inactive'" in str(exc)
