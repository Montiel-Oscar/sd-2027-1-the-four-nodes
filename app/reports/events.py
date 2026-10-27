"""Feed interno del outbox; alertas lo consulta sin compartir la base de reportes."""

import os
from datetime import datetime, timezone
from secrets import compare_digest
from uuid import UUID

from fastapi import Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.reports.models import OutboxEventV1, PendingReportEvent
from app.reports.schemas import InternalEvent, InternalEventBatch


def require_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    expected = os.getenv("INTERNAL_API_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="API interna no configurada")
    if x_internal_token is None or not compare_digest(x_internal_token, expected):
        raise HTTPException(status_code=403, detail="Token interno inválido")


def _utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _to_public(event: OutboxEventV1 | PendingReportEvent) -> InternalEvent:
    route = "extravios" if event.type == "missing_pet.reported" else "hallazgos"
    return InternalEvent(
        id=event.id,
        report_id=event.report_id,
        type=event.type,
        municipality=event.municipality,
        created_at=event.created_at,
        public_url=f"/reportes/{route}/{event.report_id}",
    )


def pending_events(session: Session, limit: int) -> InternalEventBatch:
    old = list(
        session.scalars(
            select(PendingReportEvent)
            .where(PendingReportEvent.processed_at.is_(None))
            .order_by(PendingReportEvent.created_at, PendingReportEvent.id)
            .limit(limit)
        )
    )
    new = list(
        session.scalars(
            select(OutboxEventV1)
            .where(OutboxEventV1.processed_at.is_(None))
            .order_by(OutboxEventV1.created_at, OutboxEventV1.id)
            .limit(limit)
        )
    )
    ordered = sorted(old + new, key=lambda event: (_utc(event.created_at), str(event.id)))
    return InternalEventBatch(events=[_to_public(event) for event in ordered[:limit]])


def acknowledge_event(session: Session, event_id: UUID) -> None:
    with session.begin():
        event = session.get(OutboxEventV1, event_id)
        if event is None:
            event = session.get(PendingReportEvent, event_id)
        if event is None:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        if event.processed_at is None:
            event.processed_at = datetime.now(timezone.utc)
