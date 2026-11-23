"""API pública de reportes y feed interno para el proceso de alertas."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_actor_id
from app.core.db import get_session
from app.reports.events import acknowledge_event, pending_events, require_internal_token
from app.reports.models import FoundPetReport, MissingPetReport
from app.reports.schemas import (
    FoundPetInput,
    FoundPetPublic,
    InternalEventBatch,
    MissingPetInput,
    MissingPetPublic,
    PetDetails,
)
from app.reports.service import (
    get_public_found_pet,
    get_public_report,
    list_found_pets,
    list_missing_pets,
    publish_found_pet,
    publish_missing_pet,
)

router = APIRouter(prefix="/api/reportes", tags=["reportes"])


def _public(report: MissingPetReport, request: Request) -> MissingPetPublic:
    return MissingPetPublic(
        id=report.id,
        public_url=str(request.url_for("public_report", report_id=report.id)),
        pet=PetDetails(
            name=report.pet_name, species=report.pet_species, traits=report.pet_traits
        ),
        seen_at=report.seen_at,
        municipality=report.municipality,
        neighborhood=report.neighborhood,
        landmark=report.landmark,
        public_phone=report.public_phone if report.show_phone else None,
        created_at=report.created_at,
    )


def _public_found(report: FoundPetReport, request: Request) -> FoundPetPublic:
    return FoundPetPublic(
        id=report.id,
        public_url=str(request.base_url).rstrip("/") + f"/reportes/hallazgos/{report.id}",
        description=report.description,
        seen_at=report.seen_at,
        municipality=report.municipality,
        neighborhood=report.neighborhood,
        landmark=report.landmark,
        public_phone=report.public_phone if report.show_phone else None,
        created_at=report.created_at,
    )


@router.post(
    "/extravios", response_model=MissingPetPublic, status_code=status.HTTP_201_CREATED
)
def create_missing_pet(
    data: MissingPetInput,
    request: Request,
    idempotency_key: str = Header(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"),
    actor_id: UUID = Depends(get_actor_id),
    session: Session = Depends(get_session),
) -> MissingPetPublic:
    report = publish_missing_pet(session, actor_id, idempotency_key, data)
    return _public(report, request)


@router.get("/extravios/{report_id}", response_model=MissingPetPublic, name="get_missing_pet")
def get_missing_pet(
    report_id: UUID, request: Request, session: Session = Depends(get_session)
) -> MissingPetPublic:
    return _public(get_public_report(session, report_id), request)


@router.get("/extravios", response_model=list[MissingPetPublic])
def list_missing_reports(
    request: Request,
    municipality: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> list[MissingPetPublic]:
    return [_public(report, request) for report in list_missing_pets(session, municipality)]


@router.post(
    "/hallazgos", response_model=FoundPetPublic, status_code=status.HTTP_201_CREATED
)
def create_found_pet(
    data: FoundPetInput,
    request: Request,
    idempotency_key: str = Header(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"),
    actor_id: UUID = Depends(get_actor_id),
    session: Session = Depends(get_session),
) -> FoundPetPublic:
    report = publish_found_pet(session, actor_id, idempotency_key, data)
    return _public_found(report, request)


@router.get("/hallazgos/{report_id}", response_model=FoundPetPublic)
def get_found_pet(
    report_id: UUID, request: Request, session: Session = Depends(get_session)
) -> FoundPetPublic:
    return _public_found(get_public_found_pet(session, report_id), request)


@router.get("/hallazgos", response_model=list[FoundPetPublic])
def list_found_reports(
    request: Request,
    municipality: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> list[FoundPetPublic]:
    return [_public_found(report, request) for report in list_found_pets(session, municipality)]


@router.get(
    "/internal/events",
    response_model=InternalEventBatch,
    dependencies=[Depends(require_internal_token)],
)
def get_pending_events(
    limit: int = Query(default=50, ge=1, le=50),
    session: Session = Depends(get_session),
) -> InternalEventBatch:
    return pending_events(session, limit)


@router.post(
    "/internal/events/{event_id}/ack",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_internal_token)],
)
def ack_pending_event(event_id: UUID, session: Session = Depends(get_session)) -> None:
    acknowledge_event(session, event_id)
