"""Datos que reportes posee durante el monolito y al separar alertas."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
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
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
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
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
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


class ReportConversation(Base):
    __tablename__ = "report_conversations"
    __table_args__ = (
        UniqueConstraint("report_kind", "report_id", "participant_id", name="uq_report_conversation_participant"),
        Index("ix_report_conversations_owner", "owner_id"),
        Index("ix_report_conversations_participant", "participant_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    report_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    report_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    participant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ReportMessage(Base):
    __tablename__ = "report_messages"
    __table_args__ = (Index("ix_report_messages_conversation_created", "conversation_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("report_conversations.id"), nullable=False)
    sender_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
