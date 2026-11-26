"""Servicio de identidad con base propia y el mismo contrato HTTP público."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import get_engine
from app.identity.models import User
from app.identity.router import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    User.__table__.create(bind=get_engine(), checkfirst=True)
    yield


app = FastAPI(title="Servicio de identidad", version="1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Base de identidad no disponible") from exc
    return {"status": "ready"}
