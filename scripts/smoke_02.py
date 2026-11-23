"""Prueba HTTP de la separación; ejecutar con `docker compose up -d` activo."""

import json
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from uuid import uuid4


def api(port: int, method: str, path: str, payload=None, headers=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        f"http://localhost:{port}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urlopen(request, timeout=5) as response:
        content = response.read()
        return response.status, json.loads(content) if content else None


assert api(8000, "GET", "/health/ready")[0] == 200
assert api(8001, "GET", "/health/ready")[0] == 200
suffix = uuid4().hex[:12]
municipality = f"Demo {suffix}"
password = "clave-de-prueba-123"


def account(label):
    credentials = {"email": f"smoke-{label}-{suffix}@example.org", "password": password}
    assert api(8000, "POST", "/api/usuarios/register", credentials)[0] == 201
    token = api(8000, "POST", "/api/usuarios/login", credentials)[1]["access_token"]
    return {"Authorization": f"Bearer {token}"}


publisher = account("publisher")
recipient = account("recipient")
assert api(8001, "POST", "/api/alertas/subscriptions", {"municipality": municipality}, recipient)[0] == 201

report_data = {
    "description": "Perro con collar azul",
    "seen_at": datetime.now(timezone.utc).isoformat(),
    "municipality": municipality,
    "neighborhood": "Centro",
    "landmark": "Frente al parque",
    "show_phone": False,
}
report_headers = {**publisher, "Idempotency-Key": f"smoke-{suffix}"}
first = api(8000, "POST", "/api/reportes/hallazgos", report_data, report_headers)
assert first[0] == 201
assert api(8000, "POST", "/api/reportes/hallazgos", report_data, report_headers)[1]["id"] == first[1]["id"]
assert api(8000, "GET", f'/api/reportes/hallazgos/{first[1]["id"]}')[0] == 200

deadline = time.monotonic() + 35
while time.monotonic() < deadline:
    inbox = api(8001, "GET", "/api/alertas/inbox", headers=recipient)[1]
    matching = [alert for alert in inbox if alert["public_url"].endswith(first[1]["id"])]
    if matching:
        assert len(matching) == 1
        assert matching[0]["type"] == "found_pet.reported"
        break
    time.sleep(1)
else:
    raise AssertionError("La alerta no llegó en 35 segundos")

assert api(8001, "GET", "/api/alertas/inbox", headers=publisher)[1] == []
print("OK: identidad, hallazgo idempotente, dos bases, entrega HTTP y bandeja privada")
