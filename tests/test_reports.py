"""Pruebas del contrato de Oscar sin esperar la rama de mascotas de Luisa."""

from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import String, Uuid, create_engine, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_actor_id
from app.core.db import Base, get_session
from app.reports import service
from app.reports.models import MissingPetReport, PendingReportEvent
from app.reports.router import router
from app.web.router import router as web_router

DEMO_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


class ExamplePet(Base):
    __tablename__ = "example_pets_for_reports_tests"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    species: Mapped[str] = mapped_column(String(60), nullable=False)
    traits: Mapped[str] = mapped_column(String(500), nullable=False)


@pytest.fixture
def setup(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(
        engine, tables=[ExamplePet.__table__, MissingPetReport.__table__, PendingReportEvent.__table__]
    )
    factory = sessionmaker(engine)

    def fake_resolve(session, owner_id, data):
        if data.pet is not None:
            pet = ExamplePet(owner_id=owner_id, **data.pet.model_dump())
            session.add(pet)
            session.flush()
            return pet
        pet = session.scalar(
            select(ExamplePet).where(
                ExamplePet.id == data.pet_id, ExamplePet.owner_id == owner_id
            )
        )
        if pet is None:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
        return pet

    def session_dependency():
        with factory() as session:
            yield session

    monkeypatch.setattr(service, "_resolve_pet", fake_resolve)
    app = FastAPI()
    app.include_router(web_router)
    app.include_router(router)
    app.dependency_overrides[get_session] = session_dependency
    app.dependency_overrides[get_actor_id] = lambda: DEMO_USER_ID
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, factory
    engine.dispose()


def payload(**changes):
    result = {
        "pet": {"name": "Luna", "species": "perro", "traits": "pelaje café"},
        "seen_at": "2026-10-12T18:00:00-06:00",
        "municipality": "Coyoacán",
        "neighborhood": "Del Carmen",
        "landmark": "Cerca del parque",
    }
    result.update(changes)
    return result


def count(factory, model):
    with factory() as session:
        return session.scalar(select(func.count()).select_from(model))


def test_publication_retry_and_public_link(setup):
    client, factory = setup
    headers = {"Idempotency-Key": "intento-luna-1"}
    first = client.post("/api/reportes/extravios", json=payload(), headers=headers)
    assert first.status_code == 201, first.text
    repeated = client.post("/api/reportes/extravios", json=payload(), headers=headers)
    assert repeated.status_code == 201
    assert repeated.json() == first.json()
    assert client.get(first.json()["public_url"]).status_code == 200
    assert client.get(f'/api/reportes/extravios/{first.json()["id"]}').json() == first.json()
    assert count(factory, ExamplePet) == 1
    assert count(factory, MissingPetReport) == 1
    assert count(factory, PendingReportEvent) == 1
    with factory() as session:
        event = session.scalar(select(PendingReportEvent))
        assert event.report_id == UUID(first.json()["id"])
        assert event.municipality == "Coyoacán"
        assert event.processed_at is None


def test_key_conflict_and_phone_consent(setup):
    client, factory = setup
    headers = {"Idempotency-Key": "intento-luna-2"}
    data = payload(public_phone=" 555 123 4567 ", show_phone=False)
    first = client.post("/api/reportes/extravios", json=data, headers=headers)
    assert first.status_code == 201
    assert first.json()["public_phone"] is None
    assert client.get(f'/api/reportes/extravios/{first.json()["id"]}').json()["public_phone"] is None
    changed = client.post(
        "/api/reportes/extravios", json=payload(landmark="Otra calle"), headers=headers
    )
    assert changed.status_code == 409
    assert count(factory, MissingPetReport) == 1
    assert count(factory, PendingReportEvent) == 1


def test_existing_pet_must_belong_to_actor(setup):
    client, factory = setup
    with factory.begin() as session:
        own = ExamplePet(
            owner_id=DEMO_USER_ID, name="Sol", species="gato", traits="blanco"
        )
        other = ExamplePet(
            owner_id=uuid4(), name="Nube", species="gato", traits="gris"
        )
        session.add_all([own, other])
        session.flush()
        own_id, other_id = own.id, other.id

    own_report = client.post(
        "/api/reportes/extravios",
        json=payload(pet=None, pet_id=str(own_id)),
        headers={"Idempotency-Key": "mi-gato"},
    )
    assert own_report.status_code == 201, own_report.text
    assert own_report.json()["pet"]["name"] == "Sol"
    forbidden = client.post(
        "/api/reportes/extravios",
        json=payload(pet=None, pet_id=str(other_id)),
        headers={"Idempotency-Key": "gato-ajeno"},
    )
    assert forbidden.status_code == 404
    assert count(factory, MissingPetReport) == 1


def test_event_failure_rolls_back_pet_and_report(setup, monkeypatch):
    client, factory = setup

    def fail_event(**_values):
        raise RuntimeError("No se pudo preparar el evento")

    monkeypatch.setattr(service, "PendingReportEvent", fail_event)
    response = client.post(
        "/api/reportes/extravios",
        json=payload(),
        headers={"Idempotency-Key": "evento-falla"},
    )
    assert response.status_code == 500
    assert count(factory, ExamplePet) == 0
    assert count(factory, MissingPetReport) == 0
    assert count(factory, PendingReportEvent) == 0


def test_invalid_request_is_not_saved(setup):
    client, factory = setup
    response = client.post(
        "/api/reportes/extravios",
        json=payload(pet=None, show_phone=True),
        headers={"Idempotency-Key": "invalido"},
    )
    assert response.status_code == 422
    assert count(factory, MissingPetReport) == 0
