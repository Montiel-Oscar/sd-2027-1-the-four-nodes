"""API pública de reportes y feed interno para el proceso de alertas."""

from typing import Literal
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_actor_id
from app.core.db import get_session
from app.reports.events import acknowledge_event, pending_events, require_internal_token
from app.reports.conversations import list_conversations, list_messages, send_message, start_conversation
from app.reports.models import FoundPetReport, MissingPetReport, ReportPhoto
from app.reports.schemas import (
    FoundPetInput,
    FoundPetPublic,
    InternalEventBatch,
    MissingPetInput,
    MissingPetPublic,
    MessageInput,
    MessagePublic,
    ConversationPublic,
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


def _photo_url(session: Session, kind: str, report_id: UUID) -> str | None:
    exists = session.scalar(select(ReportPhoto.id).where(
        ReportPhoto.report_kind == kind, ReportPhoto.report_id == report_id
    ))
    return f"/api/reportes/{kind}/{report_id}/foto" if exists else None


def _public(report: MissingPetReport, request: Request, session: Session) -> MissingPetPublic:
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
        latitude=report.latitude,
        longitude=report.longitude,
        public_phone=report.public_phone if report.show_phone else None,
        photo_url=_photo_url(session, "extravios", report.id),
        created_at=report.created_at,
    )


def _public_found(report: FoundPetReport, request: Request, session: Session) -> FoundPetPublic:
    return FoundPetPublic(
        id=report.id,
        public_url=str(request.base_url).rstrip("/") + f"/reportes/hallazgos/{report.id}",
        description=report.description,
        seen_at=report.seen_at,
        municipality=report.municipality,
        neighborhood=report.neighborhood,
        landmark=report.landmark,
        latitude=report.latitude,
        longitude=report.longitude,
        public_phone=report.public_phone if report.show_phone else None,
        photo_url=_photo_url(session, "hallazgos", report.id),
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
    return _public(report, request, session)


@router.get("/extravios/{report_id}", response_model=MissingPetPublic, name="get_missing_pet")
def get_missing_pet(
    report_id: UUID, request: Request, session: Session = Depends(get_session)
) -> MissingPetPublic:
    return _public(get_public_report(session, report_id), request, session)


@router.get("/extravios", response_model=list[MissingPetPublic])
def list_missing_reports(
    request: Request,
    municipality: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> list[MissingPetPublic]:
    return [_public(report, request, session) for report in list_missing_pets(session, municipality)]


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
    return _public_found(report, request, session)


@router.get("/hallazgos/{report_id}", response_model=FoundPetPublic)
def get_found_pet(
    report_id: UUID, request: Request, session: Session = Depends(get_session)
) -> FoundPetPublic:
    return _public_found(get_public_found_pet(session, report_id), request, session)


@router.get("/hallazgos", response_model=list[FoundPetPublic])
def list_found_reports(
    request: Request,
    municipality: str | None = Query(default=None, max_length=120),
    session: Session = Depends(get_session),
) -> list[FoundPetPublic]:
    return [_public_found(report, request, session) for report in list_found_pets(session, municipality)]


@router.put("/{kind}/{report_id}/foto", status_code=204)
async def upload_report_photo(
    kind: Literal["extravios", "hallazgos"], report_id: UUID, request: Request,
    actor_id: UUID = Depends(get_actor_id), session: Session = Depends(get_session),
) -> Response:
    model = MissingPetReport if kind == "extravios" else FoundPetReport
    report = session.get(model, report_id)
    if report is None or report.owner_id != actor_id:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "image/jpeg":
        raise HTTPException(status_code=415, detail="Selecciona una imagen JPG")
    try:
        advertised_size = int(request.headers.get("content-length", "0") or "0")
    except ValueError:
        raise HTTPException(status_code=400, detail="Tamaño de archivo inválido") from None
    if advertised_size > 3_000_000:
        raise HTTPException(status_code=413, detail="La imagen debe pesar menos de 3 MB")
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 3_000_000:
            raise HTTPException(status_code=413, detail="La imagen debe pesar menos de 3 MB")
    if not raw:
        raise HTTPException(status_code=413, detail="La imagen debe pesar menos de 3 MB")
    try:
        with Image.open(BytesIO(raw)) as source:
            if source.format != "JPEG" or source.width * source.height > 16_000_000:
                raise ValueError("Imagen JPG inválida o demasiado grande")
            clean = ImageOps.exif_transpose(source).convert("RGB")
            output = BytesIO()
            clean.save(output, format="JPEG", quality=85, optimize=True)
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=422, detail="El archivo no es una imagen JPG válida") from None
    photo = session.scalar(select(ReportPhoto).where(
        ReportPhoto.report_kind == kind, ReportPhoto.report_id == report_id
    ))
    if photo is None:
        photo = ReportPhoto(report_kind=kind, report_id=report_id, jpeg_data=output.getvalue())
        session.add(photo)
    else:
        photo.jpeg_data = output.getvalue()
    session.commit()
    return Response(status_code=204)


@router.get("/{kind}/{report_id}/foto", response_class=Response)
def get_report_photo(
    kind: Literal["extravios", "hallazgos"], report_id: UUID,
    session: Session = Depends(get_session),
) -> Response:
    photo = session.scalar(select(ReportPhoto).where(
        ReportPhoto.report_kind == kind, ReportPhoto.report_id == report_id
    ))
    if photo is None:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return Response(content=photo.jpeg_data, media_type="image/jpeg", headers={"X-Content-Type-Options":"nosniff", "Cache-Control":"public, max-age=300"})


@router.post("/{kind}/{report_id}/conversaciones", response_model=ConversationPublic, status_code=201)
def contact_report_owner(
    kind: Literal["extravios", "hallazgos"], report_id: UUID, data: MessageInput,
    actor_id: UUID = Depends(get_actor_id), session: Session = Depends(get_session),
) -> ConversationPublic:
    return start_conversation(session, kind, report_id, actor_id, data.body)


@router.get("/conversaciones", response_model=list[ConversationPublic])
def my_conversations(
    actor_id: UUID = Depends(get_actor_id), session: Session = Depends(get_session),
) -> list[ConversationPublic]:
    return list_conversations(session, actor_id)


@router.get("/conversaciones/{conversation_id}/mensajes", response_model=list[MessagePublic])
def conversation_messages(
    conversation_id: UUID, actor_id: UUID = Depends(get_actor_id),
    session: Session = Depends(get_session),
) -> list[MessagePublic]:
    return list_messages(session, conversation_id, actor_id)


@router.post("/conversaciones/{conversation_id}/mensajes", response_model=MessagePublic, status_code=201)
def reply_to_conversation(
    conversation_id: UUID, data: MessageInput, actor_id: UUID = Depends(get_actor_id),
    session: Session = Depends(get_session),
) -> MessagePublic:
    return send_message(session, conversation_id, actor_id, data.body)


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
