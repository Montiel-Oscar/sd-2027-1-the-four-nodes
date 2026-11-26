"""Sesión y metadata de identidad, mascotas y reportes."""

import os
from functools import lru_cache
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta DATABASE_URL; inicia con Docker Compose o configúrala localmente")
    return create_engine(url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session


def init_db() -> None:
    # Reportes conserva solo mascotas y reportes; identidad posee otra base.
    from app.pets.models import Pet
    from app.reports.models import (
        FoundPetReport, MissingPetReport, OutboxEventV1, PendingReportEvent,
    )

    Base.metadata.create_all(
        bind=get_engine(),
        tables=[
            Pet.__table__, MissingPetReport.__table__, PendingReportEvent.__table__,
            FoundPetReport.__table__, OutboxEventV1.__table__,
        ],
    )
