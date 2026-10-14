"""API pública de extravíos de la primera entrega."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_actor_id
from app.core.db import get_session
from app.reports.models import MissingPetReport
from app.reports.schemas import MissingPetInput, MissingPetPublic, PetDetails
from app.reports.service import get_public_report, publish_missing_pet

router = APIRouter(prefix="/api/reportes", tags=["reportes"])


def _public(report: MissingPetReport, request: Request) -> MissingPetPublic:
    return MissingPetPublic(
        id=report.id,
        public_url=str(request.url_for("get_missing_pet", report_id=report.id)),
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
