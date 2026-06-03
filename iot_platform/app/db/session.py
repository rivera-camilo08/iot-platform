import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,
    pool_pre_ping=True,
)

if settings.environment == "testing" or settings.DATABASE_URL.startswith("sqlite"):
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def wait_for_database(max_retries: int = 30, delay_seconds: int = 2) -> None:
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            return
        except OperationalError as error:
            last_error = error
            print(f"Waiting for database availability (attempt {attempt}/{max_retries})...")
            time.sleep(delay_seconds)

    raise RuntimeError(
        "Unable to connect to the database after multiple retries. "
        "Check DATABASE_URL, PostgreSQL availability, and network configuration. "
        f"Last error: {last_error}"
    )
