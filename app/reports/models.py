"""Datos que reportes posee durante el monolito y al separar alertas."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class MissingPetReport(Base):
    __tablename__ = "missing_pet_reports"
    __table_args__ = (
        UniqueConstraint("owner_id", "idempotency_key", name="uq_missing_report_attempt"),
        Index("ix_missing_reports_municipality_created", "municipality", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    pet_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    pet_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pet_species: Mapped[str] = mapped_column(String(60), nullable=False)
    pet_traits: Mapped[str] = mapped_column(String(500), nullable=False)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), nullable=False)
    landmark: Mapped[str] = mapped_column(String(250), nullable=False)
    public_phone: Mapped[str | None] = mapped_column(String(32))
    show_phone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class PendingReportEvent(Base):
    """Eventos de extravío creados en 01-monolito; se conservan para migrar sin borrar datos."""

    __tablename__ = "pending_report_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("missing_pet_reports.id"), nullable=False, unique=True
    )
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class FoundPetReport(Base):
    __tablename__ = "found_pet_reports"
    __table_args__ = (
        UniqueConstraint("owner_id", "idempotency_key", name="uq_found_report_attempt"),
        Index("ix_found_reports_municipality_created", "municipality", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), nullable=False)
    landmark: Mapped[str] = mapped_column(String(250), nullable=False)
    public_phone: Mapped[str | None] = mapped_column(String(32))
    show_phone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )


class OutboxEventV1(Base):
    """Eventos nuevos de ambos tipos, independientes de la tabla de reporte."""

    __tablename__ = "outbox_events_v1"
    __table_args__ = (
        UniqueConstraint("type", "report_id", name="uq_outbox_report_type"),
        Index("ix_outbox_pending_created", "processed_at", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
