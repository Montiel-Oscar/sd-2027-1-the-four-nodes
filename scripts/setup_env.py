"""Genera las claves locales requeridas por Compose sin mostrarlas en pantalla."""

from pathlib import Path
from secrets import token_hex


def main() -> None:
    target = Path(__file__).resolve().parents[1] / ".env"
    if target.exists():
        lines = target.read_text().splitlines()
        keys = {
            line.split("=", 1)[0]: line.split("=", 1)[1]
            for line in lines
            if "=" in line and not line.lstrip().startswith("#")
        }
        changed = False
        for name in ("POSTGRES_PASSWORD", "AUTH_SECRET", "INTERNAL_API_TOKEN"):
            if not keys.get(name):
                changed = True
                replacement = f"{name}={token_hex(32)}"
                for index, line in enumerate(lines):
                    if line.startswith(f"{name}="):
                        lines[index] = replacement
                        break
                else:
                    lines.append(replacement)
        if changed:
            target.write_text("\n".join(lines) + "\n")
        target.chmod(0o600)
        print(".env existente conservado; se completaron las claves vacías si las había.")
    else:
        target.write_text(
            "# Generado para desarrollo local; no subir a Git.\n"
            + "\n".join(
                f"{name}={token_hex(32)}"
                for name in ("POSTGRES_PASSWORD", "AUTH_SECRET", "INTERNAL_API_TOKEN")
            )
            + "\n"
        )
        target.chmod(0o600)
        print(".env creado con tres claves aleatorias.")


if __name__ == "__main__":
    main()
