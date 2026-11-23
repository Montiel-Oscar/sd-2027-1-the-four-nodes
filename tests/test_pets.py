from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_actor_id
from app.core.db import Base, get_session
from app.pets.router import router as pets_router


def _build_client(current_actor_id: UUID):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(pets_router)

    def override_get_session():
        db: Session = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_actor_id() -> UUID:
        return current_actor_id

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_actor_id] = override_get_actor_id
    return TestClient(app), engine


def test_create_list_get_and_update_own_pet():
    owner_id = uuid4()
    client, engine = _build_client(owner_id)

    create_resp = client.post(
        "/api/mascotas",
        json={"name": "Luna", "species": "perro", "traits": "pelaje café"},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    pet_id = created["id"]
    assert created["name"] == "Luna"

    list_resp = client.get("/api/mascotas")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["id"] == pet_id

    get_resp = client.get(f"/api/mascotas/{pet_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["traits"] == "pelaje café"

    update_resp = client.put(
        f"/api/mascotas/{pet_id}",
        json={
            "name": "Luna",
            "species": "perro",
            "traits": "pelaje café con collar azul",
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["traits"] == "pelaje café con collar azul"

    engine.dispose()


def test_cannot_get_or_update_another_owners_pet():
    owner_a = uuid4()
    owner_b = uuid4()
    client_a, engine = _build_client(owner_a)

    create_resp = client_a.post(
        "/api/mascotas",
        json={"name": "Michi", "species": "gato", "traits": "gris atigrado"},
    )
    assert create_resp.status_code == 201
    pet_id = create_resp.json()["id"]

    # Cambiamos el actor inyectado al segundo dueño sobre el mismo motor SQLite en memoria
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app_b = FastAPI()
    app_b.include_router(pets_router)

    def override_get_session():
        db: Session = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app_b.dependency_overrides[get_session] = override_get_session
    app_b.dependency_overrides[get_actor_id] = lambda: owner_b
    client_b = TestClient(app_b)

    assert client_b.get("/api/mascotas").json() == []
    assert client_b.get(f"/api/mascotas/{pet_id}").status_code == 404
    assert (
        client_b.put(
            f"/api/mascotas/{pet_id}",
            json={"name": "Michi", "species": "gato", "traits": "editado ajeno"},
        ).status_code
        == 404
    )

    engine.dispose()
