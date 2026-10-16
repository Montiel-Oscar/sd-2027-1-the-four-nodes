"""Punto de entrada del monolito. Cada equipo agrega rutas en su propio módulo."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.alerts.router import router as alerts_router
from app.core.db import get_engine, init_db
from app.identity.router import router as identity_router
from app.pets.router import router as pets_router
from app.reports.router import router as reports_router
from app.web.router import router as web_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="The Four Nodes", version="0.1.0", lifespan=lifespan)

app.include_router(web_router)
app.include_router(identity_router)
app.include_router(pets_router)
app.include_router(reports_router)
app.include_router(alerts_router)


@app.get("/health/live", tags=["salud"])
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["salud"])
def ready() -> dict[str, str]:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from exc
    return {"status": "ready"}
