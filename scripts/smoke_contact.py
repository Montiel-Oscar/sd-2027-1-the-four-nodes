"""Prueba HTTP de mensajes privados. Crea datos ficticios en el volumen local."""

import json
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


def api(method, path, payload=None, token=None, key=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if key:
        headers["Idempotency-Key"] = key
    request = Request(
        "http://localhost:8000" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


suffix = uuid4().hex[:12]
password = "clave-de-contacto-123"


def account(role):
    credentials = {"email": f"contact-{role}-{suffix}@example.org", "password": password}
    assert api("POST", "/api/usuarios/register", credentials)[0] == 201
    return api("POST", "/api/usuarios/login", credentials)[1]["access_token"]


owner, finder, stranger = account("owner"), account("finder"), account("stranger")
report = api(
    "POST", "/api/reportes/extravios",
    {
        "pet": {"name": "Luna", "species": "perro", "traits": "collar azul"},
        "seen_at": datetime.now(timezone.utc).isoformat(),
        "municipality": "Demo contacto " + suffix,
        "neighborhood": "Centro", "landmark": "Parque",
        "show_phone": False,
    }, token=owner, key="contact-" + suffix,
)
assert report[0] == 201, report
report_id = report[1]["id"]
assert report[1]["public_phone"] is None
start = f"/api/reportes/extravios/{report_id}/conversaciones"
assert api("POST", start, {"body": "La vi junto al parque"})[0] == 401
assert api("POST", start, {"body": "Hola"}, token=owner)[0] == 403
first = api("POST", start, {"body": "La vi junto al parque"}, token=finder)
assert first[0] == 201, first
conversation_id = first[1]["id"]
messages = f"/api/reportes/conversaciones/{conversation_id}/mensajes"
assert api("GET", messages, token=stranger)[0] == 404
owner_list = api("GET", "/api/reportes/conversaciones", token=owner)
assert owner_list[0] == 200 and any(row["id"] == conversation_id for row in owner_list[1])
assert api("POST", messages, {"body": "Gracias, voy hacia allá"}, token=owner)[0] == 201
finder_messages = api("GET", messages, token=finder)
assert finder_messages[0] == 200
assert [row["sender_is_me"] for row in finder_messages[1]] == [True, False]
assert [row["body"] for row in finder_messages[1]] == ["La vi junto al parque", "Gracias, voy hacia allá"]
print("OK: contacto privado sin teléfono, respuesta y acceso exclusivo de dos cuentas")
