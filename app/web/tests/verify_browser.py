"""Prueba de interfaz con Edge y APIs simuladas: python app/web/tests/verify_browser.py.

Requiere playwright y Microsoft Edge. No sustituye la demo con PostgreSQL.
"""
import json
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

STATIC = Path(__file__).resolve().parents[1] / "static"
REPORT_ID = "12345678-1234-1234-1234-123456789abc"


def main():
    calls = []
    fail_publication = True
    inbox_calls = 0
    errors = []
    pets = []
    next_error = 0

    def serve(route):
        nonlocal fail_publication, inbox_calls, next_error
        request = route.request
        if request.url.startswith("https://tile.openstreetmap.org/"):
            route.fulfill(status=204)
            return
        assert request.url.startswith("http://localhost:8000/"), request.url
        path = request.url.split("localhost:8000")[-1].split("localhost:8001")[-1]
        path = path.split("?")[0]
        headers = {"Access-Control-Allow-Origin": "http://localhost:8000"}
        if request.method == "OPTIONS":
            route.fulfill(status=204, headers={**headers, "Access-Control-Allow-Headers": "authorization,content-type", "Access-Control-Allow-Methods": "GET,POST,DELETE"})
            return
        if path.startswith("/api/"):
            calls.append((path, request.method, request.headers, request.post_data))
            data = []
            status = 200
            if next_error:
                code, next_error = next_error, 0
                route.fulfill(status=code, json={"detail":"Error de prueba"})
                return
            if path == "/api/mascotas":
                if request.method == "POST":
                    data = {"id":REPORT_ID, **json.loads(request.post_data)}
                    pets.append(data)
                    status = 201
                else:
                    data = pets if request.headers.get("authorization") == "Bearer test-session-token" else []
            elif path.endswith("/register"):
                data = {"id": REPORT_ID, "email": "amy@example.org"}
                status = 201
            elif path.endswith("/login"):
                data = {"access_token": "test-session-token", "token_type": "bearer"}
            elif path.endswith("/subscriptions"):
                data = [{"id": REPORT_ID, "municipality": "Coyoacán"}]
            elif path.endswith("/inbox"):
                inbox_calls += 1
                data = [{"type": "found_pet.reported", "municipality": "Coyoacán", "public_url": f"/reportes/hallazgos/{REPORT_ID}", "created_at": "2026-11-12T12:00:00Z"}]
            elif request.method == "POST" and "/reportes/" in path:
                if fail_publication:
                    fail_publication = False
                    route.abort("failed")
                    return
                data = {"id": REPORT_ID}
                status = 201
            elif path.endswith(REPORT_ID):
                data = {"description": "<img src=x onerror=alert(1)>", "municipality": "Coyoacán", "neighborhood": "Centro", "landmark": "Parque", "seen_at": "2026-11-12T12:00:00Z", "public_phone": None}
            route.fulfill(status=status, json=data, headers=headers)
            return
        file = "community.html" if path == "/comunidad" else "index.html" if path == "/" else "report.html" if path.startswith("/reportes/") else path.removeprefix("/web/")
        target = STATIC / file
        if target.is_file():
            mime = "text/javascript" if target.suffix == ".js" else "text/css" if target.suffix == ".css" else "image/jpeg" if target.suffix == ".jpg" else "text/html"
            route.fulfill(body=target.read_bytes(), content_type=mime)
        else:
            route.fulfill(status=404)

    with sync_playwright() as playwright:
        browser_path = os.getenv("PLAYWRIGHT_BROWSER")
        browser = playwright.chromium.launch(
            executable_path=browser_path, headless=True
        ) if browser_path else playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.clock.install()
        page.route("**/*", serve)
        page.goto("http://localhost:8000/comunidad")
        for width in (390, 768, 1440):
            page.set_viewport_size({"width": width, "height": 1000})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), width
        page.locator('[name="email"]').fill("amy@example.org")
        page.locator('[name="password"]').fill("test-password")
        page.get_by_role("button", name="Crear cuenta", exact=True).click()
        expect(page.locator("#account-status")).to_contain_text("Cuenta creada")
        page.locator('[name="password"]').fill("test-password")
        page.get_by_role("button", name="Entrar", exact=True).click()
        expect(page.locator("#session-state")).to_have_text("Sesión iniciada")
        expect(page.locator("#inbox a")).to_have_attribute("href", f"/reportes/hallazgos/{REPORT_ID}")
        assert page.evaluate("localStorage.length") == 0
        pet_form = page.locator("#pet-form")
        pet_form.locator('[name="name"]').fill("Luna")
        pet_form.locator('[name="species"]').select_option("perro")
        pet_form.locator('[name="traits"]').fill("Collar azul")
        pet_form.get_by_role("button").click()
        expect(page.locator("#pets-list h3")).to_have_text("Luna")
        assert not any(call[1] == "POST" and "/reportes/" in call[0] for call in calls)
        form = page.locator("#found-form")
        for name, value in {"description":"Perro con collar rojo", "seen_at":"2026-11-12T10:30", "municipality":"Coyoacán", "neighborhood":"Centro", "landmark":"Parque"}.items():
            form.locator(f'[name="{name}"]').fill(value)
        page.locator("#found-map").click(position={"x":180,"y":140})
        form.get_by_role("button", name="Publicar hallazgo").click()
        expect(page.locator("#found-status")).to_contain_text("No pudimos conectar")
        form.get_by_role("button", name="Publicar hallazgo").click()
        expect(page.locator("#found-success")).to_be_visible()
        publications = [call for call in calls if call[0].endswith("/hallazgos") and call[1] == "POST"]
        assert publications[0][2]["idempotency-key"] == publications[1][2]["idempotency-key"]
        assert publications[0][2]["authorization"] == "Bearer test-session-token"
        assert "public_phone" not in json.loads(publications[0][3])
        form.locator('[name="show_phone"]').check()
        form.locator('[name="public_phone"]').fill("5551234567")
        form.get_by_role("button", name="Publicar hallazgo").click()
        expect(page.locator("#found-success")).to_be_visible()
        latest = [call for call in calls if call[0].endswith("/hallazgos") and call[1] == "POST"][-1]
        assert latest[2]["idempotency-key"] != publications[0][2]["idempotency-key"]
        assert json.loads(latest[3])["public_phone"] == "5551234567"
        next_error = 409
        form.get_by_role("button", name="Publicar hallazgo").click()
        expect(page.locator("#found-status")).to_contain_text("Conflicto")
        page.locator("#subscription-form input").fill("Coyoacán")
        page.locator("#subscription-form button").click()
        expect(page.locator("#subscriptions-status")).to_contain_text("reportes nuevos")
        assert any(call[0].endswith("/subscriptions") and call[1] == "POST" and call[2].get("authorization") == "Bearer test-session-token" for call in calls)
        before = inbox_calls
        page.clock.fast_forward(31000)
        expect(page.locator("#inbox-status")).to_have_text("Bandeja actualizada.")
        expect(page).to_have_url("http://localhost:8000/comunidad")
        time.sleep(0.2)
        page.evaluate("0")
        assert inbox_calls > before
        page.get_by_role("button", name="Cerrar sesión").click()
        expect(page.locator("#inbox")).to_be_empty()
        expect(page.locator("#pets-list")).to_be_empty()
        assert page.evaluate("sessionStorage.length") == 0
        page.goto(f"http://localhost:8000/reportes/hallazgos/{REPORT_ID}")
        expect(page.locator("#pet-traits")).to_have_text("<img src=x onerror=alert(1)>")
        expect(page.locator("#contact")).to_be_hidden()
        expect(page.locator("#report-map-unavailable")).to_be_visible()
        assert page.locator("#pet-traits img").count() == 0
        page.goto("http://localhost:8000/")
        page.locator(".inline-account summary").click()
        page.locator('#account-form [name="email"]').fill("amy@example.org")
        page.locator('#account-form [name="password"]').fill("test-password")
        page.locator('#account-form button[value="login"]').click()
        expect(page.locator("#session-state")).to_have_text("Sesión iniciada")
        form = page.locator("#publish-form")
        form.locator('[name="name"]').fill("Luna")
        form.locator('[name="species"]').select_option("perro")
        form.locator('[name="traits"]').fill("Collar azul")
        page.locator("#wizard-next").click()
        for name, value in {"seen_at":"2026-11-12T10:30", "municipality":"Coyoacán", "neighborhood":"Centro", "landmark":"Parque"}.items():
            form.locator(f'[name="{name}"]').fill(value)
        page.locator("#wizard-next").click()
        expect(page.locator("#status")).to_contain_text("Haz clic en el mapa")
        page.locator("#missing-map").click(position={"x":180,"y":140})
        page.locator("#wizard-next").click()
        page.locator("#wizard-next").click()
        fail_publication = True
        form.locator('button[type="submit"]').click()
        expect(page.locator("#status")).to_contain_text("No pudimos conectar")
        form.locator('button[type="submit"]').click()
        expect(page.locator("#success")).to_be_visible()
        missing = [call for call in calls if call[0].endswith("/extravios") and call[1] == "POST"]
        assert missing[0][2]["authorization"] == "Bearer test-session-token"
        assert missing[0][2]["idempotency-key"] == missing[1][2]["idempotency-key"]
        page.goto(f"http://localhost:8000/?pet_id={REPORT_ID}")
        expect(page.locator("#saved-pet")).to_have_value(REPORT_ID)
        expect(page.locator('#publish-form [name="name"]')).to_be_disabled()
        page.locator("#wizard-next").click()
        for name, value in {"seen_at":"2026-11-15T10:30", "municipality":"Coyoacán", "neighborhood":"Centro", "landmark":"Parque"}.items():
            page.locator(f'#publish-form [name="{name}"]').fill(value)
        page.locator("#missing-map").click(position={"x":180,"y":140})
        page.locator("#wizard-next").click()
        page.locator("#wizard-next").click()
        page.locator('#publish-form button[type="submit"]').click()
        expect(page.locator("#success")).to_be_visible()
        existing = [call for call in calls if call[0].endswith("/extravios") and call[1] == "POST"][-1]
        assert json.loads(existing[3])["pet_id"] == REPORT_ID
        assert "pet" not in json.loads(existing[3])
        page.goto("http://localhost:8000/comunidad")
        expect(page.locator("#pets-list h3")).to_have_text("Luna")
        next_error = 401
        page.locator("#refresh-pets").click()
        expect(page.locator("#session-state")).to_contain_text("Inicia sesión")
        expect(page.locator("#pets-list")).to_be_empty()
        page.get_by_role("link", name="Cuenta", exact=True).focus()
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.textContent") == "Mis mascotas"
        assert not errors, errors
        browser.close()
    print("OK: registro, JWT, hallazgo y extravío con reintentos, consentimiento, suscripción, polling, cierre de sesión, reporte público y 3 anchos.")


if __name__ == "__main__":
    main()
