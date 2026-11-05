"""Registro, inicio de sesión y consulta de la cuenta autenticada."""

from functools import lru_cache
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import create_access_token, get_actor_id, invalid_credentials
from app.core.db import get_session
from app.identity.models import User

class IdentityRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def handle(request):
            try:
                return await handler(request)
            except RequestValidationError as exc:
                # Los errores de validación no deben devolver credenciales.
                errors = [
                    {key: error[key] for key in ("loc", "msg", "type")}
                    for error in exc.errors()
                ]
                return JSONResponse(status_code=422, content={"detail": errors})

        return handle


router = APIRouter(prefix="/api/usuarios", tags=["usuarios"], route_class=IdentityRoute)
password_hash = PasswordHash.recommended()


class Credentials(BaseModel):
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: SecretStr = Field(min_length=8, max_length=1024)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str


class TokenPublic(BaseModel):
    access_token: str
    token_type: str = "bearer"


@lru_cache(maxsize=1)
def dummy_password_hash() -> str:
    # También verificamos un hash cuando el correo no existe.
    return password_hash.hash("cuenta-inexistente-no-autenticar")


@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: Credentials, session: Session = Depends(get_session)):
    user = User(email=data.email, password_hash=password_hash.hash(data.password.get_secret_value()))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="El correo ya está registrado") from None
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenPublic)
def login(data: Credentials, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.email == data.email))
    stored_hash = user.password_hash if user is not None else dummy_password_hash()
    valid = password_hash.verify(data.password.get_secret_value(), stored_hash)
    if user is None or not valid:
        raise invalid_credentials()
    return TokenPublic(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserPublic)
def current_user(
    actor_id: UUID = Depends(get_actor_id), session: Session = Depends(get_session)
):
    user = session.get(User, actor_id)
    if user is None:
        raise invalid_credentials()
    return user
