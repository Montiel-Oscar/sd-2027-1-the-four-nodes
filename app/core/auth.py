"""Actor de demostración para `01-monolito`; identidad lo sustituirá después."""

from uuid import UUID

DEMO_USER_ID = UUID("00000000-0000-4000-8000-000000000001")


def get_actor_id() -> UUID:
    """Entrega el mismo actor a identidad, mascotas y reportes.

    En esta etapa no autentica credenciales: todos los visitantes comparten
    la cuenta demo. Los consumidores deben usar Depends(get_actor_id), sin
    copiar el UUID, para poder sustituir esta dependencia por autenticación.
    """
    return DEMO_USER_ID
