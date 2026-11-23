"""Comprueba balanceo, aislamiento del outbox y continuidad tras una réplica caída."""

import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import urlopen


BASE = "http://localhost:8000"


def request(path: str) -> tuple[int, str | None]:
    try:
        with urlopen(BASE + path, timeout=5) as response:
            return response.status, response.headers.get("X-Report-Instance")
    except HTTPError as error:
        return error.code, error.headers.get("X-Report-Instance")
    except OSError:
        return 0, None


def wait_for_replica(name: str, limit: int = 15) -> None:
    deadline = time.monotonic() + limit
    while time.monotonic() < deadline:
        if all(request("/health/ready") == (200, name) for _ in range(4)):
            return
        time.sleep(0.5)
    raise AssertionError(f"Traefik no aisló la réplica caída; se esperaba {name}")


def main() -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and request("/health/ready")[0] != 200:
        time.sleep(0.5)
    assert request("/api/reportes/internal/events")[0] == 404
    instances = set()
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline and instances != {"reportes_a", "reportes_b"}:
        instance = request("/health/ready")[1]
        if instance:
            instances.add(instance)
        time.sleep(0.2)
    assert instances == {"reportes_a", "reportes_b"}, instances
    subprocess.run(["docker", "compose", "stop", "reportes_a"], check=True)
    try:
        wait_for_replica("reportes_b")
        subprocess.run([sys.executable, "scripts/smoke_02.py"], check=True)
    finally:
        subprocess.run(["docker", "compose", "start", "reportes_a"], check=True)
    print("OK: dos réplicas, outbox privado y publicación/alerta con una réplica detenida")


if __name__ == "__main__":
    main()
