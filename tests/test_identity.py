from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.auth import DEMO_USER_ID
from app.identity.router import router


def test_demo_actor_is_stable():
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        first = client.get("/api/usuarios/me")
        second = client.get("/api/usuarios/me")
    assert first.status_code == 200
    assert first.json() == second.json() == {"id": str(DEMO_USER_ID), "mode": "demo"}
