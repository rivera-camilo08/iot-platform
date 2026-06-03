from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.db.wait_for_db import wait_for_database
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            campo = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
            errors.append({
                "campo": campo or "body",
                "error": error["msg"],
                "valor_recibido": error.get("input"),
            })
        return JSONResponse(
            status_code=422,
            content={
                "detalle": "Error de validación en los datos enviados",
                "errores": errors,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "detalle": "Error interno del servidor",
                "error": str(exc),
            },
        )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()


@app.on_event("startup")
def startup_event() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        wait_for_database()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# En producción se debe ejecutar:
#   alembic upgrade head
# antes de iniciar la aplicación.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
