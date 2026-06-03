import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings


def wait_for_database(max_retries: int = 30, delay_seconds: int = 2) -> None:
    """Wait until the configured database is responsive.

    This is used by Docker container startup and FastAPI startup events.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        return

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return
        except OperationalError as error:
            last_error = error
            print(
                f"Database unavailable (attempt {attempt}/{max_retries}). "
                f"Retrying in {delay_seconds}s..."
            )
            time.sleep(delay_seconds)

    raise RuntimeError(
        "Unable to connect to PostgreSQL after multiple retries. "
        "Verify DATABASE_URL, network connectivity, and PostgreSQL readiness. "
        f"Last error: {last_error}"
    )


if __name__ == "__main__":
    wait_for_database()
