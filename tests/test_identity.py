"""Contratos de identidad y autorización de la segunda entrega."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, Uuid, create_engine, select
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import TOKEN_ISSUER, create_access_token, get_actor_id
from app.core.db import get_session
from app.identity.models import User
from app.identity.router import password_hash, router as identity_router
from app.pets.models import Pet
from app.pets.router import router as pets_router
from app.reports.models import MissingPetReport, PendingReportEvent
from app.reports.router import router as reports_router
from app.web.router import router as web_router

TEST_SECRET = "secreto-de-pruebas-de-al-menos-32-bytes"
PASSWORD = "clave-de-prueba-123"


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET", TEST_SECRET)
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # Solo el esquema de prueba adapta UUID PostgreSQL a CHAR para SQLite.
    metadata = MetaData()
    for table in (User.__table__, Pet.__table__, MissingPetReport.__table__, PendingReportEvent.__table__):
        copied = table.to_metadata(metadata)
        for column in copied.columns:
            if isinstance(column.type, PostgreSQLUUID):
                column.type = Uuid(as_uuid=True)
    metadata.create_all(engine)
    factory = sessionmaker(engine)

    def session_dependency():
        with factory() as session:
            yield session

    app = FastAPI()
    for router in (identity_router, pets_router, reports_router, web_router):
        app.include_router(router)
    app.dependency_overrides[get_session] = session_dependency
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def account(client, email="persona@example.org"):
    result = client.post("/api/usuarios/register", json={"email": email, "password": PASSWORD})
    assert result.status_code == 201, result.text
    login = client.post("/api/usuarios/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200, login.text
    assert login.json()["token_type"] == "bearer"
    return result.json(), {"Authorization": "Bearer " + login.json()["access_token"]}


def test_register_login_me_and_hash(setup):
    client, factory = setup
    user, headers = account(client, "  Persona@Example.ORG  ")
    assert set(user) == {"id", "email"}
    assert user["email"] == "persona@example.org"
    UUID(user["id"])
    assert client.get("/api/usuarios/me", headers=headers).json() == user
    with factory() as session:
        saved = session.get(User, UUID(user["id"]))
        assert saved.password_hash.startswith("$argon2id$")
        assert saved.password_hash != PASSWORD
        assert password_hash.verify(PASSWORD, saved.password_hash)
        assert saved.created_at is not None
    duplicate = client.post("/api/usuarios/register", json={
        "email": "PERSONA@example.org", "password": "otra-clave-123"
    })
    assert duplicate.status_code == 409
    with factory() as session:
        assert len(session.scalars(select(User)).all()) == 1
    assert client.get("/api/usuarios/me", headers=headers).json() == user


def test_bad_credentials_do_not_reveal_account(setup):
    client, _ = setup
    account(client)
    wrong = client.post("/api/usuarios/login", json={
        "email": "persona@example.org", "password": "clave-equivocada"
    })
    missing = client.post("/api/usuarios/login", json={
        "email": "nadie@example.org", "password": "clave-equivocada"
    })
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json() == missing.json()
    assert wrong.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("body", [
    {"email": "sin-correo", "password": PASSWORD},
    {"email": "a@example.org", "password": "corta"},
    {"email": "a@example.org", "password": "a" * 1025},
])
def test_invalid_registration(setup, body):
    client, _ = setup
    for endpoint in ("register", "login"):
        response = client.post("/api/usuarios/" + endpoint, json=body)
        assert response.status_code == 422
        assert body["password"] not in response.text


@pytest.mark.parametrize("header", [None, "Basic abc", "Bearer", "Bearer basura"])
def test_private_routes_require_bearer(setup, header):
    client, _ = setup
    headers = {"Authorization": header} if header else {}
    for route in ("/api/usuarios/me", "/api/mascotas"):
        result = client.get(route, headers=headers)
        assert result.status_code == 401
        assert result.headers["www-authenticate"] == "Bearer"
    report = client.post("/api/reportes/extravios", headers={
        **headers, "Idempotency-Key": "sin-token"
    }, json={
        "pet": {"name": "Luna", "species": "perro", "traits": "cafe"},
        "seen_at": "2026-10-30T12:00:00-06:00", "municipality": "Coyoacan",
        "neighborhood": "Del Carmen", "landmark": "Parque"
    })
    assert report.status_code == 401


@pytest.mark.parametrize("invalid", [
    "expired", "issuer", "subject", "missing_exp", "missing_sub", "missing_iss",
    "signature", "algorithm", "tampered"
])
def test_reject_invalid_tokens(setup, invalid):
    client, _ = setup
    claims = {"sub": str(uuid4()), "iss": TOKEN_ISSUER,
              "exp": datetime.now(timezone.utc) + timedelta(minutes=60)}
    key, algorithm = TEST_SECRET, "HS256"
    if invalid == "expired":
        claims["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    elif invalid == "issuer":
        claims["iss"] = "otro-emisor"
    elif invalid == "subject":
        claims["sub"] = "no-es-uuid"
    elif invalid.startswith("missing_"):
        claims.pop(invalid.removeprefix("missing_"))
    elif invalid == "signature":
        key = "otro-secreto-con-longitud-de-32-bytes"
    elif invalid == "algorithm":
        algorithm = "HS384"
        key = "a" * 64
    token = jwt.encode(claims, key, algorithm=algorithm)
    if invalid == "tampered":
        parts = token.split(".")
        parts[1] = parts[1][:-2] + "xx"
        token = ".".join(parts)
    result = client.get("/api/mascotas", headers={"Authorization": "Bearer " + token})
    assert result.status_code == 401


def test_token_claims_and_verifier_without_database(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET", TEST_SECRET)
    actor = uuid4()
    before = datetime.now(timezone.utc).timestamp()
    token = create_access_token(actor)
    after = datetime.now(timezone.utc).timestamp()
    claims = jwt.decode(token, TEST_SECRET, algorithms=["HS256"], issuer=TOKEN_ISSUER)
    assert claims["sub"] == str(actor)
    assert before + 3599 <= claims["exp"] <= after + 3600
    assert jwt.get_unverified_header(token)["alg"] == "HS256"
    # Segundo proceso FastAPI que solo importa get_actor_id, como alertas.
    app = FastAPI()

    @app.get("/actor")
    def actor_endpoint(actor_id: UUID = Depends(get_actor_id)):
        return {"id": str(actor_id)}

    def no_database():
        raise AssertionError("El verificador no debe abrir una sesión")

    app.dependency_overrides[get_session] = no_database
    with TestClient(app) as client:
        result = client.get("/actor", headers={"Authorization": "Bearer " + token})
    assert result.status_code == 200
    assert result.json() == {"id": str(actor)}


@pytest.mark.parametrize("secret", ["", "corto"])
def test_missing_or_short_secret_fails_closed(setup, monkeypatch, secret):
    client, _ = setup
    _, headers = account(client)
    monkeypatch.setenv("AUTH_SECRET", secret)
    assert client.get("/api/mascotas", headers=headers).status_code == 503
    assert client.post("/api/usuarios/login", json={
        "email": "persona@example.org", "password": PASSWORD
    }).status_code == 503


def test_me_rejects_token_without_existing_account(setup):
    client, _ = setup
    result = client.get("/api/usuarios/me", headers={
        "Authorization": "Bearer " + create_access_token(uuid4())
    })
    assert result.status_code == 401


def test_two_users_own_pets_and_reports(setup):
    client, factory = setup
    user_a, headers_a = account(client, "a@example.org")
    _, headers_b = account(client, "b@example.org")
    with factory() as session:
        hashes = session.scalars(select(User.password_hash)).all()
        assert len(set(hashes)) == 2  # Misma contraseña, sal distinta por cuenta.
    pet = client.post("/api/mascotas", headers=headers_a, json={
        "name": "Luna", "species": "perro", "traits": "pelaje cafe"
    })
    assert pet.status_code == 201, pet.text
    pet_id = pet.json()["id"]
    assert client.get("/api/mascotas", headers=headers_a).json() == [pet.json()]
    assert client.get("/api/mascotas", headers=headers_b).json() == []
    assert client.get("/api/mascotas/" + pet_id, headers=headers_b).status_code == 404
    data = {"pet_id": pet_id, "seen_at": "2026-10-30T12:00:00-06:00",
            "municipality": "Coyoacan", "neighborhood": "Del Carmen", "landmark": "Parque"}
    assert client.post("/api/reportes/extravios", headers={
        **headers_b, "Idempotency-Key": "intento-ajeno"
    }, json=data).status_code == 404
    report = client.post("/api/reportes/extravios", headers={
        **headers_a, "Idempotency-Key": "intento-propio"
    }, json=data)
    assert report.status_code == 201, report.text
    with factory() as session:
        saved = session.get(MissingPetReport, UUID(report.json()["id"]))
        assert saved.owner_id == UUID(user_a["id"])
    # Los reportes son públicos; nunca exponen identidad interna ni credenciales.
    public = client.get("/api/reportes/extravios/" + report.json()["id"])
    assert public.status_code == 200
    assert not {"owner_id", "password", "password_hash"}.intersection(public.json())
