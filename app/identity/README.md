# Cecilia · identidad de la primera entrega

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/cecilia-identidad`. En GitHub Desktop, selecciona la rama base, actualízala y crea tu rama personal.

El [PRD](../../docs/PRD.md) permite una cuenta de demostración en esta rama. Revisa `app/core/auth.py` y deja una dependencia `get_actor_id` estable para Oscar y Luisa. Si añades registro e inicio de sesión, deben seguir siendo parte de **esta única aplicación y base**; no crees otro servicio todavía.

**Entregable mínimo:** un actor de demostración consistente y una prueba que muestre que las operaciones privadas reciben su ID. Documenta cómo sustituirlo por autenticación real. Si completas registro e inicio de sesión, añade pruebas de contraseña incorrecta y de acceso sin sesión. Publica tu rama y solicita integración hacia `01-monolito`.

## Estado integrado

No se recibió una rama o solicitud de integración de Cecilia para esta etapa. Se completó el mínimo con el actor fijo de `app/core/auth.py`, `GET /api/usuarios/me` y `tests/test_identity.py`. Toda publicación y ficha usa `get_actor_id`; las cuentas reales, credenciales y tokens quedan para las ramas posteriores del PRD. Esta cuenta de demostración es compartida por todos los visitantes locales.

## Trabajo de Ceci en `02-separacion`

Crea `trabajo/ceci-identidad-v1` desde `02-separacion`. En esta etapa implementa usuarios reales con correo, hash Argon2id, login y token firmado; identidad aún vive dentro de `app` y de su base. Conserva `get_actor_id` para reportes, mascotas y alertas. Sigue los pasos de [PLAN_02_SEPARACION.md](../../docs/PLAN_02_SEPARACION.md#ceci--identidad-trabajoceci-identidad-v1) y el contrato de [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md#identidad-ceci--oscar-luisa-y-amy). Prueba 401 sin token, clave incorrecta, expiración y propiedad entre dos usuarios. Publica PR con base `02-separacion`.
