"""Tablas exclusivas de la base lógica four_nodes_alerts."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.alerts.db import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (UniqueConstraint("recipient_id", "municipality", name="uq_recipient_municipality"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    recipient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (UniqueConstraint("event_id", "recipient_id", name="uq_event_recipient"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    recipient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    public_url: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
