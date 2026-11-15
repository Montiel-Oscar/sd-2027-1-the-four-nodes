"""Recorrido con dos cuentas: APIs reales en SQLite local o --base-url de Traefik.

Requiere dependencias del proyecto y playwright. La modalidad local no prueba Docker.
"""
import argparse
import json
import os
import re
import secrets
import sys
import tempfile
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from playwright.sync_api import expect, sync_playwright


@contextmanager
def local_api():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from sqlalchemy import MetaData, Uuid, create_engine
    from sqlalchemy.dialects.postgresql import UUID as PGUUID
    from sqlalchemy.orm import Session
    from sqlalchemy.pool import StaticPool

    with tempfile.TemporaryDirectory() as temporary:
        os.environ["AUTH_SECRET"] = secrets.token_urlsafe(40)
        os.environ["INTERNAL_API_TOKEN"] = secrets.token_urlsafe(32)
        os.environ["DATABASE_URL_ALERTS"] = "sqlite:///" + (Path(temporary) / "alerts.sqlite3").as_posix()
        from app.core.db import Base, get_session
        from app.identity.router import router as identity
        from app.pets.router import router as pets
        from app.reports.router import router as reports
        from app.web.router import router as web
        from app.alerts import main as alerts
        from app.alerts.db import Base as AlertsBase, engine as alerts_engine

        engine = create_engine("sqlite://", connect_args={"check_same_thread":False}, poolclass=StaticPool)
        metadata = MetaData()
        for table in Base.metadata.tables.values():
            copied = table.to_metadata(metadata)
            for column in copied.columns:
                if isinstance(column.type, PGUUID):
                    column.type = Uuid(as_uuid=True)
        metadata.create_all(engine)
        AlertsBase.metadata.create_all(alerts_engine)

        def session():
            with Session(engine) as db:
                yield db

        app = FastAPI()
        for router in (identity, pets, reports, web, alerts.app.router):
            app.include_router(router)
        @asynccontextmanager
        async def test_lifespan(_app):
            # Los eventos se procesan explícitamente; no iniciar el worker de red.
            yield
        app.router.lifespan_context = test_lifespan
        app.dependency_overrides[get_session] = session

        async def deliver():
            import httpx
            headers = {"X-Internal-Token":os.environ["INTERNAL_API_TOKEN"]}
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://app") as client:
                pending = await client.get("/api/reportes/internal/events", headers=headers)
                pending.raise_for_status()
                for event in pending.json()["events"]:
                    # Ejecuta lógica real, incluida reentrega, sin worker temporizado ni red.
                    await alerts.process_event(client, event, headers["X-Internal-Token"])
                    await alerts.process_event(client, event, headers["X-Internal-Token"])

        with TestClient(app) as client:
            def route(request_route):
                request = request_route.request
                path = urlsplit(request.url)
                response = client.request(request.method, path.path + ("?" + path.query if path.query else ""), content=request.post_data_buffer, headers={key:value for key,value in request.headers.items() if key in ("authorization","content-type","idempotency-key")})
                if request.method == "POST" and path.path in ("/api/reportes/extravios", "/api/reportes/hallazgos") and response.status_code == 201:
                    client.portal.call(deliver)
                request_route.fulfill(status=response.status_code, body=response.content, content_type=response.headers.get("content-type", "application/json"))
            try:
                yield route
            finally:
                engine.dispose()
                alerts_engine.dispose()


def run(browser, base, output, transport=None):
    errors = []
    requests = []
    contexts = [browser.new_context(viewport={"width":1440,"height":1000}, timezone_id="America/Mexico_City") for _ in range(2)]
    pages = [context.new_page() for context in contexts]
    for page in pages:
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url))
        if transport:
            page.route("**/*", transport)
    a, b = pages
    suffix = uuid4().hex[:10]
    municipality = "Demo " + suffix
    password = secrets.token_urlsafe(16)

    def account(page, label):
        page.goto(base + "/comunidad")
        page.locator('#account-form [name="email"]').fill(f"demo-{label}-{suffix}@example.org")
        page.locator('#account-form [name="password"]').fill(password)
        page.get_by_role("button", name="Crear cuenta", exact=True).click()
        expect(page.locator("#account-status")).to_contain_text("Cuenta creada")
        page.locator('#account-form [name="password"]').fill(password)
        page.get_by_role("button", name="Entrar", exact=True).click()
        expect(page.locator("#session-state")).to_have_text("Sesión iniciada")

    account(a, "dueno")
    account(b, "vecino")
    expect(b.locator("#inbox-status")).to_contain_text("vacía")
    b.locator("#subscription-form input").fill(municipality)
    b.locator("#subscription-form button").click()
    expect(b.locator("#subscriptions li")).to_have_count(1)
    pet = a.locator("#pet-form")
    pet.locator('[name="name"]').fill("Luna")
    pet.locator('[name="species"]').select_option("perro")
    pet.locator('[name="traits"]').fill("Pelaje café, collar azul")
    pet.get_by_role("button").click()
    expect(a.locator("#pets-list h3")).to_have_text("Luna")
    a.locator("#pets").screenshot(path=str(output / "01-ficha-propia.png"))
    b.locator("#refresh-pets").click()
    expect(b.locator("#pets-status")).to_contain_text("Todavía no tienes")
    expect(b.locator("#pets-list")).to_be_empty()
    own_link = a.locator("#pets-list a").get_attribute("href")
    from urllib.parse import parse_qs
    pet_id = parse_qs(urlsplit(own_link).query)["pet_id"][0]
    assert b.evaluate("""async id => (await fetch('/api/mascotas/' + id, {headers:window.FourNodes.authHeaders()})).status""", pet_id) == 404
    a.locator("#pets-list a").click()
    expect(a.locator('#publish-form [name="name"]')).to_have_value("Luna")
    expect(a.locator('#publish-form [name="name"]')).to_be_disabled()

    def publish_missing(page, new=False):
        form = page.locator("#publish-form")
        if new:
            page.goto(base + "/")
            form.locator('[name="name"]').fill("Sol")
            form.locator('[name="species"]').select_option("gato")
            form.locator('[name="traits"]').fill("Pelaje blanco, collar rojo")
        page.locator("#wizard-next").click()
        for name,value in {"seen_at":datetime.now().strftime("%Y-%m-%dT%H:%M"),"municipality":municipality,"neighborhood":"Centro","landmark":"Entrada del parque"}.items():
            form.locator(f'[name="{name}"]').fill(value)
        page.locator("#wizard-next").click()
        page.locator("#wizard-next").click()
        form.locator('button[type="submit"]').click()
        expect(page.locator("#success")).to_be_visible()
        return page.locator("#public-link").get_attribute("href")

    missing_url = publish_missing(a)
    # La segunda cuenta también puede crear ficha y reporte juntos.
    publish_missing(b, new=True)
    b.goto(base + "/comunidad")
    expect(b.locator("#pets-list h3")).to_have_text("Sol")
    found = b.locator("#found-form")
    for name,value in {"description":"Perro con collar azul junto al parque","seen_at":datetime.now().strftime("%Y-%m-%dT%H:%M"),"municipality":municipality,"neighborhood":"Centro","landmark":"Fuente del parque"}.items():
        found.locator(f'[name="{name}"]').fill(value)
    found.locator('[name="show_phone"]').check()
    found.locator('[name="public_phone"]').fill("5550000000")
    found.get_by_role("button").click()
    expect(b.locator("#found-success")).to_be_visible()
    found_url = b.locator("#found-link").get_attribute("href")
    b.locator("#filter-form input").fill(municipality)
    b.locator("#filter-form button").click()
    expect(b.locator("#reports-list article")).to_have_count(3)
    b.locator("#refresh-alerts").click()
    # En vivo, el trabajador y la consulta de la página pueden tardar.
    expect(b.locator("#inbox a")).to_have_count(3, timeout=180000)
    b.locator("#alerts").screenshot(path=str(output / "04-suscripcion-bandeja.png"))
    b.set_viewport_size({"width":390,"height":844})
    for path in ("/comunidad", "/"):
        b.goto(base + path)
        assert b.evaluate("document.documentElement.scrollWidth <= innerWidth"), path
    b.screenshot(path=str(output / "05-movil-390.png"), full_page=True)
    for name,url in (("02-extravio-publico.png",missing_url),("03-hallazgo-publico.png",found_url)):
        public_context = browser.new_context(viewport={"width":1280,"height":900}, timezone_id="America/Mexico_City")
        page = public_context.new_page()
        if transport:
            page.route("**/*", transport)
        page.goto(base + url if url.startswith("/") else url)
        expect(page.locator("#report")).to_be_visible()
        page.get_by_role("button", name="Copiar enlace").click()
        expect(page.locator("#status")).to_contain_text(re.compile(r"Enlace copiado\.|Copia este enlace:"))
        if "extravio" in name:
            expect(page.locator("#contact")).to_be_hidden()
        else:
            expect(page.locator("#phone")).to_have_text("5550000000")
        page.screenshot(path=str(output / name), full_page=True)
        public_context.close()
    b.goto(base + "/comunidad")
    b.get_by_role("button", name="Dejar de seguir " + municipality, exact=True).click()
    expect(b.locator("#subscriptions li")).to_have_count(0)
    b.get_by_role("button", name="Cerrar sesión").click()
    for selector in ("#pets-list", "#subscriptions", "#inbox"):
        expect(b.locator(selector)).to_be_empty()
    assert all(urlsplit(url).netloc == urlsplit(base).netloc for url in requests)
    assert not errors, errors
    for context in contexts:
        context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", help="Origen real de Traefik; omitir para APIs locales SQLite mediante TestClient")
    parser.add_argument("--output", default="docs/pitch/capturas")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    # Si un nuevo ensayo falla, no conservar un sello de éxito del ensayo anterior.
    (output / "entorno.json").unlink(missing_ok=True)
    with sync_playwright() as playwright:
        browser_path = os.getenv("PLAYWRIGHT_BROWSER")
        browser = playwright.chromium.launch(executable_path=browser_path, headless=True) if browser_path else playwright.chromium.launch(channel="msedge", headless=True)
        if args.base_url:
            run(browser, args.base_url.rstrip("/"), output)
        else:
            with local_api() as transport:
                run(browser, "http://localhost:8000", output, transport)
        browser.close()
    (output / "entorno.json").write_text(json.dumps({"fecha_utc":datetime.now(timezone.utc).isoformat(), "entorno":"Traefik en vivo" if args.base_url else "APIs reales via TestClient, SQLite temporal; sin Docker, red ni balanceo", "browser":os.getenv("PLAYWRIGHT_BROWSER", "Microsoft Edge"), "resultado":"Dos cuentas aisladas; ficha separada, reutilizada y creada con reporte; hallazgo; alertas; privacidad; móvil; origen único"}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: recorrido final con dos cuentas y capturas; consultar entorno.json para los límites de evidencia.")


if __name__ == "__main__":
    main()
