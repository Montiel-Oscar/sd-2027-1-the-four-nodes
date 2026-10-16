"""Sesión y metadata compartidas solo en la etapa monolítica."""

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
    # Importar los modelos para registrar sus tablas en la metadata común.
    from app.alerts import models as alerts_models  # noqa: F401
    from app.identity import models as identity_models  # noqa: F401
    from app.pets import models as pets_models  # noqa: F401
    from app.reports import models as reports_models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
