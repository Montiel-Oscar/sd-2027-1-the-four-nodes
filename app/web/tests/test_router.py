from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.web.router import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_form_and_assets_are_served():
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="publish-form"' in response.text
    assert 'name="show_phone"' in response.text
    assert client.get("/web/app.js").status_code == 200
    assert client.get("/web/style.css").status_code == 200


def test_public_page_validates_report_id():
    response = client.get("/reportes/extravios/12345678-1234-1234-1234-123456789abc")
    assert response.status_code == 200
    assert 'id="report"' in response.text
    assert client.get("/reportes/extravios/invalid").status_code == 422


def test_distributed_pages_and_scripts():
    response = client.get("/comunidad")
    assert response.status_code == 200
    for form in ("account-form", "found-form", "subscription-form", "filter-form"):
        assert f'id="{form}"' in response.text
    for script in ("session.js", "community.js"):
        assert client.get(f"/web/{script}").status_code == 200
    assert client.get("/reportes/hallazgos/12345678-1234-1234-1234-123456789abc").status_code == 200
    assert client.get("/reportes/hallazgos/invalid").status_code == 422


def test_photo_route_does_not_serve_arbitrary_files():
    assert client.get("/web/photos/session.js").status_code == 404
