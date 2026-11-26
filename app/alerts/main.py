"""Servicio de alertas: consume el outbox de reportes por HTTP."""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.alerts.db import Base, SessionLocal, engine, get_db
from app.alerts.models import Alert, Subscription
from app.core.auth import get_actor_id

logger = logging.getLogger(__name__)
INTERNAL_API_URL = os.getenv("INTERNAL_API_URL", "http://app:8000/api/reportes")


def utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


async def process_event(client: httpx.AsyncClient, event: dict, token: str) -> None:
    event_id = UUID(event["id"])
    created_at = utc(datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")))
    with SessionLocal() as db:
        subscribers = db.scalars(
            select(Subscription).where(Subscription.municipality == event["municipality"])
        ).all()
        for subscription in subscribers:
            if utc(subscription.created_at) > created_at:
                continue
            already_sent = db.scalar(
                select(Alert.id).where(
                    Alert.event_id == event_id,
                    Alert.recipient_id == subscription.recipient_id,
                )
            )
            if already_sent is None:
                db.add(
                    Alert(
                        event_id=event_id,
                        recipient_id=subscription.recipient_id,
                        type=event["type"],
                        municipality=event["municipality"],
                        public_url=event["public_url"],
                    )
                )
        db.commit()
    # El ACK ocurre después del commit. Un ACK perdido reintenta sin duplicar alertas.
    response = await client.post(
        f"{INTERNAL_API_URL}/internal/events/{event_id}/ack",
        headers={"X-Internal-Token": token},
    )
    response.raise_for_status()


async def alert_worker() -> None:
    while True:
        try:
            token = os.getenv("INTERNAL_API_TOKEN", "")
            if not token:
                raise RuntimeError("Falta INTERNAL_API_TOKEN")
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(
                    f"{INTERNAL_API_URL}/internal/events",
                    params={"limit": 50},
                    headers={"X-Internal-Token": token},
                )
                response.raise_for_status()
                for event in response.json()["events"]:
                    await process_event(client, event, token)
        except asyncio.CancelledError:
            raise
        except (httpx.HTTPError, SQLAlchemyError, KeyError, TypeError, ValueError, RuntimeError):
            logger.exception("No se pudo procesar el lote de alertas; se reintentará")
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    worker = asyncio.create_task(alert_worker())
    try:
        yield
    finally:
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Servicio de alertas", version="1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SubscriptionCreate(BaseModel):
    municipality: str = Field(min_length=1, max_length=120)


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    municipality: str
    created_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_id: UUID
    type: str
    municipality: str
    public_url: str
    created_at: datetime


@app.post("/api/alertas/subscriptions", response_model=SubscriptionResponse, status_code=201)
def create_subscription(
    data: SubscriptionCreate, db: Session = Depends(get_db), actor_id: UUID = Depends(get_actor_id)
):
    municipality = data.municipality.strip()
    if not municipality:
        raise HTTPException(status_code=422, detail="Municipio vacío")
    existing = db.scalar(
        select(Subscription).where(
            Subscription.recipient_id == actor_id,
            Subscription.municipality == municipality,
        )
    )
    if existing:
        return existing
    subscription = Subscription(recipient_id=actor_id, municipality=municipality)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@app.get("/api/alertas/subscriptions", response_model=list[SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db), actor_id: UUID = Depends(get_actor_id)):
    return db.scalars(
        select(Subscription)
        .where(Subscription.recipient_id == actor_id)
        .order_by(Subscription.created_at.desc())
    ).all()


@app.delete("/api/alertas/subscriptions/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    sub_id: UUID, db: Session = Depends(get_db), actor_id: UUID = Depends(get_actor_id)
):
    subscription = db.scalar(
        select(Subscription).where(
            Subscription.id == sub_id, Subscription.recipient_id == actor_id
        )
    )
    if subscription is None:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    db.delete(subscription)
    db.commit()


@app.get("/api/alertas/inbox", response_model=list[AlertResponse])
def get_inbox(db: Session = Depends(get_db), actor_id: UUID = Depends(get_actor_id)):
    return db.scalars(
        select(Alert)
        .where(Alert.recipient_id == actor_id)
        .order_by(Alert.created_at.desc())
        .limit(100)
    ).all()


@app.get("/health/live")
def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Base de alertas no disponible") from exc
    return {"status": "ready"}
