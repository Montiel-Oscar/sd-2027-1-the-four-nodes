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

def get_actor_id() -> UUID:
    """Entrega el mismo actor a identidad, mascotas y reportes.

    En esta etapa no autentica credenciales: todos los visitantes comparten
    la cuenta demo. Los consumidores deben usar Depends(get_actor_id), sin
    copiar el UUID, para poder sustituir esta dependencia por autenticación.
    """
    return DEMO_USER_ID
