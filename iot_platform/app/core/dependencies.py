from typing import Generator

from fastapi import Depends

from app.core.config import settings


def get_settings() -> Generator["Settings", None, None]:
    yield settings
