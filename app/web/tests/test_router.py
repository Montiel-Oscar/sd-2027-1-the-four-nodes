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
