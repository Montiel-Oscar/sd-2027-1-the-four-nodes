"""Identidad compartida por los routers reales del monolito."""

from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, Uuid, create_engine
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.auth import DEMO_USER_ID, get_actor_id
from app.core.db import get_session
from app.identity.router import router as identity_router
from app.pets.models import Pet
from app.pets.router import router as pets_router
from app.reports.models import MissingPetReport, PendingReportEvent
from app.reports.router import router as reports_router
from app.web.router import router as web_router


@pytest.mark.parametrize("actor_id", [DEMO_USER_ID, UUID("11111111-1111-4111-8111-111111111111")])
def test_identity_pets_and_reports_share_actor(actor_id):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # SQLite interpreta el tipo PostgreSQL UUID como numérico; usar CHAR en
    # las tablas de prueba evita perder precisión en UUID de solo dígitos.
    metadata = MetaData()
    for table in (Pet.__table__, MissingPetReport.__table__, PendingReportEvent.__table__):
        copied = table.to_metadata(metadata)
        for column in copied.columns:
            if isinstance(column.type, PostgreSQLUUID):
                column.type = Uuid(as_uuid=True)
    metadata.create_all(engine)

    def session_dependency():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    for router in (identity_router, pets_router, reports_router, web_router):
        app.include_router(router)
    app.dependency_overrides[get_session] = session_dependency
    if actor_id != DEMO_USER_ID:
        app.dependency_overrides[get_actor_id] = lambda: actor_id

    try:
        with TestClient(app) as client:
            me = client.get("/api/usuarios/me")
            assert me.status_code == 200
            assert me.json()["id"] == str(actor_id)
            pet = client.post("/api/mascotas", json={
                "name": "Luna", "species": "perro", "traits": "pelaje cafe"
            })
            assert pet.status_code == 201, pet.text
            pet_id = pet.json()["id"]
            report = client.post("/api/reportes/extravios", headers={
                "Idempotency-Key": "identidad-compartida"
            }, json={
                "pet_id": pet_id,
                "seen_at": "2026-10-12T18:00:00-06:00",
                "municipality": "Coyoacan", "neighborhood": "Del Carmen",
                "landmark": "Cerca del parque"
            })
            assert report.status_code == 201, report.text
            assert client.get("/api/mascotas").json() == [pet.json()]

            with Session(engine) as session:
                assert session.get(Pet, UUID(pet_id)).owner_id == actor_id
                saved_report = session.get(MissingPetReport, UUID(report.json()["id"]))
                assert saved_report.owner_id == actor_id
                assert saved_report.pet_id == UUID(pet_id)

            # Cambiar el actor en la dependencia basta para aislar las fichas.
            app.dependency_overrides[get_actor_id] = lambda: UUID(
                "22222222-2222-4222-8222-222222222222"
            )
            assert client.get("/api/mascotas").json() == []
            assert client.get(f"/api/mascotas/{pet_id}").status_code == 404
            # La consulta del reporte sigue siendo publica.
            assert client.get(f'/api/reportes/extravios/{report.json()["id"]}').status_code == 200
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
