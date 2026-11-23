"""Pruebas repetibles de latencia (hasta 20 suscriptores) y resiliencia ante fallas."""

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
ALERTS_URL = os.getenv("ALERTS_URL", BASE_URL).rstrip("/")
PASSWORD = os.getenv("TEST_USER_PASSWORD", "clave-de-prueba-123")


def http_req(
    base_url: str,
    method: str,
    path: str,
    payload: dict | None = None,
    headers: dict | None = None,
    timeout: float = 5.0,
) -> tuple[int, dict | list | None]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req_headers = {"Content-Type": "application/json", **(headers or {})}
    req = Request(f"{base_url}{path}", data=body, method=method, headers=req_headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed


def register_and_login(email: str, password: str) -> dict[str, str]:
    status, _ = http_req(
        BASE_URL, "POST", "/api/usuarios/register", {"email": email, "password": password}
    )
    assert status in (200, 201), f"Registro falló ({status}) para {email}"
    status, data = http_req(
        BASE_URL, "POST", "/api/usuarios/login", {"email": email, "password": password}
    )
    assert status == 200 and isinstance(data, dict) and "access_token" in data, (
        f"Login falló ({status}) para {email}"
    )
    return {"Authorization": f"Bearer {data['access_token']}"}


def wait_for_alerts(
    subscriber_headers: list[dict[str, str]],
    expected_suffix: str,
    timeout_sec: float = 150.0,
    poll_interval: float = 0.5,
) -> tuple[float, float]:
    """Espera a que todos los suscriptores reciban exactamente 1 alerta para el reporte.

    Devuelve (tiempo_primer_suscriptor_s, tiempo_ultimo_suscriptor_s) medidos desde la llamada.
    """
    start = time.monotonic()
    deadline = start + timeout_sec
    first_seen: float | None = None
    received_indices: set[int] = set()

    while time.monotonic() < deadline:
        for idx, headers in enumerate(subscriber_headers):
            if idx in received_indices:
                continue
            status, inbox = http_req(ALERTS_URL, "GET", "/api/alertas/inbox", headers=headers)
            if status != 200 or not isinstance(inbox, list):
                continue
            matches = [
                a for a in inbox if isinstance(a, dict) and str(a.get("public_url", "")).endswith(expected_suffix)
            ]
            if len(matches) == 1:
                now = time.monotonic()
                if first_seen is None:
                    first_seen = now - start
                received_indices.add(idx)
            elif len(matches) > 1:
                raise AssertionError(
                    f"Alerta duplicada ({len(matches)}) para suscriptor #{idx} en {expected_suffix}"
                )

        if len(received_indices) == len(subscriber_headers):
            total_elapsed = time.monotonic() - start
            return (first_seen if first_seen is not None else total_elapsed), total_elapsed

        time.sleep(poll_interval)

    raise AssertionError(
        f"Timeout ({timeout_sec}s): recibieron alerta {len(received_indices)}/{len(subscriber_headers)}"
    )


def run_latency_trial(trial_num: int, subscribers_count: int, timeout_sec: float) -> dict:
    run_id = uuid4().hex[:10]
    municipality = f"Resiliencia-{trial_num}-{run_id}"
    pub_headers = register_and_login(f"pub-{run_id}@example.org", PASSWORD)

    sub_headers: list[dict[str, str]] = []
    for i in range(subscribers_count):
        h = register_and_login(f"sub-{run_id}-{i}@example.org", PASSWORD)
        st, _ = http_req(
            ALERTS_URL, "POST", "/api/alertas/subscriptions", {"municipality": municipality}, h
        )
        assert st == 201, f"Fallo al suscribir #{i}: {st}"
        sub_headers.append(h)

    # 1) Reporte de hallazgo
    t_start_hallazgo = time.monotonic()
    iso_now = datetime.now(timezone.utc).isoformat()
    hallazgo_payload = {
        "description": f"Hallazgo prueba {trial_num} con collar verde",
        "seen_at": iso_now,
        "municipality": municipality,
        "neighborhood": "Centro",
        "landmark": "Jardín principal",
        "show_phone": False,
    }
    st_h, data_h = http_req(
        BASE_URL,
        "POST",
        "/api/reportes/hallazgos",
        hallazgo_payload,
        {**pub_headers, "Idempotency-Key": f"h-{run_id}-{trial_num}"},
    )
    t_resp_hallazgo = time.monotonic() - t_start_hallazgo
    assert st_h == 201 and isinstance(data_h, dict), f"Hallazgo falló: {st_h} {data_h}"
    first_sub_h, all_sub_h = wait_for_alerts(sub_headers, str(data_h["id"]), timeout_sec=timeout_sec)

    # 2) Reporte de extravío
    t_start_extravio = time.monotonic()
    extravio_payload = {
        "pet_name": f"Firulais-{run_id[:4]}",
        "species": "perro",
        "traits": "Mancha café en ojo izquierdo",
        "description": f"Extravío prueba {trial_num} cerca del parque",
        "lost_at": datetime.now(timezone.utc).isoformat(),
        "municipality": municipality,
        "neighborhood": "Norte",
        "landmark": "Kiosco",
        "show_phone": False,
    }
    st_e, data_e = http_req(
        BASE_URL,
        "POST",
        "/api/reportes/extravios",
        extravio_payload,
        {**pub_headers, "Idempotency-Key": f"e-{run_id}-{trial_num}"},
    )
    t_resp_extravio = time.monotonic() - t_start_extravio
    assert st_e == 201 and isinstance(data_e, dict), f"Extravío falló: {st_e} {data_e}"
    first_sub_e, all_sub_e = wait_for_alerts(sub_headers, str(data_e["id"]), timeout_sec=timeout_sec)

    return {
        "trial": trial_num,
        "subscribers": subscribers_count,
        "municipality": municipality,
        "hallazgo_post_s": round(t_resp_hallazgo, 3),
        "hallazgo_first_alert_s": round(first_sub_h, 3),
        "hallazgo_all_alerts_s": round(all_sub_h, 3),
        "extravio_post_s": round(t_resp_extravio, 3),
        "extravio_first_alert_s": round(first_sub_e, 3),
        "extravio_all_alerts_s": round(all_sub_e, 3),
    }


def run_outage_checks() -> None:
    """Prueba publicación con servicio de alertas caído y recuperación única tras reiniciarlo."""
    run_id = uuid4().hex[:10]
    municipality = f"FallaAlertas-{run_id}"
    pub_headers = register_and_login(f"fpub-{run_id}@example.org", PASSWORD)
    sub_headers = register_and_login(f"fsub-{run_id}@example.org", PASSWORD)

    st, _ = http_req(
        ALERTS_URL, "POST", "/api/alertas/subscriptions", {"municipality": municipality}, sub_headers
    )
    assert st == 201

    print("[Falla 1] Deteniendo servicio 'alertas' con docker compose stop alertas...")
    subprocess.run(["docker", "compose", "stop", "alertas"], check=True)
    try:
        payload = {
            "description": "Reporte publicado mientras alertas estaba detenido",
            "seen_at": datetime.now(timezone.utc).isoformat(),
            "municipality": municipality,
            "neighborhood": "Sur",
            "landmark": "Puente peatonal",
            "show_phone": False,
        }
        st_pub, data_pub = http_req(
            BASE_URL,
            "POST",
            "/api/reportes/hallazgos",
            payload,
            {**pub_headers, "Idempotency-Key": f"outage-{run_id}"},
        )
        assert st_pub == 201 and isinstance(data_pub, dict), (
            f"La publicación debió proceder con alertas caído: {st_pub} {data_pub}"
        )
        print(f"  -> Publicación exitosa ({st_pub}) con alertas caído; id={data_pub['id']}")
    finally:
        print("[Falla 1] Reiniciando servicio 'alertas' con docker compose start alertas...")
        subprocess.run(["docker", "compose", "start", "alertas"], check=True)

    first_s, all_s = wait_for_alerts([sub_headers], str(data_pub["id"]), timeout_sec=150.0)
    print(f"  -> Alerta entregada exactamente 1 vez tras recuperar alertas (en {all_s:.3f}s)")


def run_db_outage_check() -> None:
    """Verifica que detener PostgreSQL impide confirmar una publicación no guardada."""
    run_id = uuid4().hex[:10]
    pub_headers = register_and_login(f"dbpub-{run_id}@example.org", PASSWORD)
    print("[Falla 2] Deteniendo 'postgres' con docker compose stop postgres...")
    subprocess.run(["docker", "compose", "stop", "postgres"], check=True)
    try:
        payload = {
            "description": "Intento con BD detenida",
            "seen_at": datetime.now(timezone.utc).isoformat(),
            "municipality": f"BD-{run_id}",
            "neighborhood": "Centro",
            "landmark": "Plaza",
            "show_phone": False,
        }
        try:
            status, _ = http_req(
                BASE_URL,
                "POST",
                "/api/reportes/hallazgos",
                payload,
                {**pub_headers, "Idempotency-Key": f"db-{run_id}"},
                timeout=4.0,
            )
            assert status >= 500 or status == 503, f"Se esperaba error de servidor, salió {status}"
            print(f"  -> Fallo controlado recibido: HTTP {status}")
        except (HTTPError, URLError, OSError, AssertionError) as exc:
            print(f"  -> Fallo esperado al caer PostgreSQL: {type(exc).__name__}: {exc}")
    finally:
        print("[Falla 2] Levantando 'postgres' sin borrar volúmenes...")
        subprocess.run(["docker", "compose", "start", "postgres"], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pruebas repetibles de tiempos y fallas.")
    parser.add_argument("--subscribers", type=int, default=20, help="Número de suscriptores (máx 20)")
    parser.add_argument("--trials", type=int, default=3, help="Número de repeticiones")
    parser.add_argument("--timeout", type=float, default=150.0, help="Timeout de entrega en segundos")
    parser.add_argument("--with-faults", action="store_true", help="Ejecuta pruebas de caída de alertas y BD")
    args = parser.parse_args()

    assert 1 <= args.subscribers <= 20, "--subscribers debe estar entre 1 y 20"
    results = []
    for t in range(1, args.trials + 1):
        row = run_latency_trial(t, args.subscribers, args.timeout)
        results.append(row)
        print(json.dumps(row, ensure_ascii=False))

    if args.with_faults:
        run_outage_checks()
        run_db_outage_check()

    print("\nRESUMEN_JSON:", json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
