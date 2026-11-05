"""Tokens compartidos por app y alertas, sin acceso a la base de usuarios."""

import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

TOKEN_ISSUER = "the-four-nodes"
TOKEN_LIFETIME = timedelta(minutes=60)
bearer = HTTPBearer(auto_error=False)


def get_auth_secret() -> str:
    secret = os.getenv("AUTH_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AUTH_SECRET debe contener al menos 32 bytes",
        )
    return secret


def invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o vencidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_access_token(actor_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(actor_id), "iss": TOKEN_ISSUER, "exp": now + TOKEN_LIFETIME},
        get_auth_secret(),
        algorithm="HS256",
    )


def get_actor_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> UUID:
    """Verifica Bearer localmente; no importa modelos ni consulta cuentas."""
    if credentials is None:
        raise invalid_credentials()
    secret = get_auth_secret()
    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            issuer=TOKEN_ISSUER,
            options={"require": ["sub", "iss", "exp"]},
        )
        return UUID(claims["sub"])
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise invalid_credentials() from None
