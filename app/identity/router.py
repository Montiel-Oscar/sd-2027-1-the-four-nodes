"""Identidad mínima de demostración para la etapa monolítica."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.auth import get_actor_id

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("/me")
def current_user(actor_id: UUID = Depends(get_actor_id)) -> dict[str, str]:
    return {"id": str(actor_id), "mode": "demo"}
