"""Actor de demostración para `01-monolito`; identidad lo sustituirá después."""

from uuid import UUID

DEMO_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


def get_actor_id() -> UUID:
    """Dependencia de FastAPI para asociar acciones a la cuenta de demo."""
    return DEMO_USER_ID
