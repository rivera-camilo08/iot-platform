import os
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DIR / 'test.db'}")
