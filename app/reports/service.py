"""Publicación atómica e idempotente de extravíos."""

from hashlib import sha256
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.reports.models import FoundPetReport, MissingPetReport, OutboxEventV1
from app.reports.schemas import FoundPetInput, MissingPetInput


def _resolve_pet(session: Session, owner_id: UUID, data: MissingPetInput):
    # Importación local: Luisa puede implementar su módulo en paralelo.
    from app.pets.service import create_pet_for_owner, get_pet_for_owner

    if data.pet is not None:
        return create_pet_for_owner(
            session, owner_id, name=data.pet.name, species=data.pet.species, traits=data.pet.traits
        )
    pet = get_pet_for_owner(session, owner_id, data.pet_id)
    if pet is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return pet


def _existing(session: Session, owner_id: UUID, key: str) -> MissingPetReport | None:
    return session.scalar(
        select(MissingPetReport).where(
            MissingPetReport.owner_id == owner_id, MissingPetReport.idempotency_key == key
        )
    )


def _same_attempt(report: MissingPetReport, digest: str) -> MissingPetReport:
    if report.request_digest != digest:
        raise HTTPException(status_code=409, detail="Idempotency-Key ya se usó con otros datos")
    return report


def publish_missing_pet(
    session: Session, owner_id: UUID, key: str, data: MissingPetInput
) -> MissingPetReport:
    digest = sha256(data.model_dump_json(exclude_none=False).encode("utf-8")).hexdigest()
    try:
        with session.begin():
            previous = _existing(session, owner_id, key)
            if previous is not None:
                return _same_attempt(previous, digest)

            pet = _resolve_pet(session, owner_id, data)
            report = MissingPetReport(
                owner_id=owner_id,
                pet_id=pet.id,
                pet_name=pet.name,
                pet_species=pet.species,
                pet_traits=pet.traits,
                seen_at=data.seen_at,
                municipality=data.municipality,
                neighborhood=data.neighborhood,
                landmark=data.landmark,
                public_phone=data.public_phone if data.show_phone else None,
                show_phone=data.show_phone,
                idempotency_key=key,
                request_digest=digest,
            )
            session.add(report)
            session.flush()
            session.add(
                OutboxEventV1(
                    report_id=report.id,
                    type="missing_pet.reported",
                    municipality=report.municipality,
                )
            )
        return report
    except IntegrityError:
        # Una solicitud concurrente pudo confirmar la misma clave primero.
        previous = _existing(session, owner_id, key)
        if previous is not None:
            return _same_attempt(previous, digest)
        raise


def get_public_report(session: Session, report_id: UUID) -> MissingPetReport:
    report = session.get(MissingPetReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report


def list_missing_pets(session: Session, municipality: str | None) -> list[MissingPetReport]:
    query = select(MissingPetReport)
    if municipality:
        query = query.where(func.lower(MissingPetReport.municipality) == municipality.strip().lower())
    return list(
        session.scalars(query.order_by(MissingPetReport.created_at.desc(), MissingPetReport.id.desc()).limit(100))
    )


def _existing_found(session: Session, owner_id: UUID, key: str) -> FoundPetReport | None:
    return session.scalar(
        select(FoundPetReport).where(
            FoundPetReport.owner_id == owner_id, FoundPetReport.idempotency_key == key
        )
    )


def _same_found_attempt(report: FoundPetReport, digest: str) -> FoundPetReport:
    if report.request_digest != digest:
        raise HTTPException(status_code=409, detail="Idempotency-Key ya se usó con otros datos")
    return report


def publish_found_pet(
    session: Session, owner_id: UUID, key: str, data: FoundPetInput
) -> FoundPetReport:
    digest = sha256(data.model_dump_json(exclude_none=False).encode("utf-8")).hexdigest()
    try:
        with session.begin():
            previous = _existing_found(session, owner_id, key)
            if previous is not None:
                return _same_found_attempt(previous, digest)
            report = FoundPetReport(
                owner_id=owner_id,
                description=data.description,
                seen_at=data.seen_at,
                municipality=data.municipality,
                neighborhood=data.neighborhood,
                landmark=data.landmark,
                public_phone=data.public_phone if data.show_phone else None,
                show_phone=data.show_phone,
                idempotency_key=key,
                request_digest=digest,
            )
            session.add(report)
            session.flush()
            session.add(
                OutboxEventV1(
                    report_id=report.id,
                    type="found_pet.reported",
                    municipality=report.municipality,
                )
            )
        return report
    except IntegrityError:
        previous = _existing_found(session, owner_id, key)
        if previous is not None:
            return _same_found_attempt(previous, digest)
        raise


def get_public_found_pet(session: Session, report_id: UUID) -> FoundPetReport:
    report = session.get(FoundPetReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Hallazgo no encontrado")
    return report


def list_found_pets(session: Session, municipality: str | None) -> list[FoundPetReport]:
    query = select(FoundPetReport)
    if municipality:
        query = query.where(func.lower(FoundPetReport.municipality) == municipality.strip().lower())
    return list(
        session.scalars(query.order_by(FoundPetReport.created_at.desc(), FoundPetReport.id.desc()).limit(100))
    )
