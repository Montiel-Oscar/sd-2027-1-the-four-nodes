"""Copia usuarios antiguos a la base de identidad sin borrar datos previos."""

import os

from sqlalchemy import create_engine, text

from app.core.db import get_engine
from app.identity.models import User


def main() -> None:
    source_url = os.environ["LEGACY_REPORT_DATABASE_URL"]
    source = create_engine(source_url, pool_pre_ping=True)
    target = get_engine()
    User.__table__.create(bind=target, checkfirst=True)
    with source.connect() as old, target.begin() as new:
        if not old.dialect.has_table(old, "users"):
            print("No hay usuarios anteriores que migrar.")
            return
        users = old.execute(text("SELECT id, email, password_hash, created_at FROM users")).mappings()
        count = 0
        for user in users:
            new.execute(
                text("""INSERT INTO users (id, email, password_hash, created_at)
                        VALUES (:id, :email, :password_hash, :created_at)
                        ON CONFLICT (id) DO NOTHING"""),
                dict(user),
            )
            count += 1
    print(f"Migración idempotente: {count} usuarios previos examinados.")


if __name__ == "__main__":
    main()
