# Cecilia · identidad de la primera entrega

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/cecilia-identidad`. En GitHub Desktop, selecciona la rama base, actualízala y crea tu rama personal.

El [PRD](../../docs/PRD.md) permite una cuenta de demostración en esta rama. Revisa `app/core/auth.py` y deja una dependencia `get_actor_id` estable para Oscar y Luisa. Si añades registro e inicio de sesión, deben seguir siendo parte de **esta única aplicación y base**; no crees otro servicio todavía.

**Entregable mínimo:** un actor de demostración consistente y una prueba que muestre que las operaciones privadas reciben su ID. Documenta cómo sustituirlo por autenticación real. Si completas registro e inicio de sesión, añade pruebas de contraseña incorrecta y de acceso sin sesión. Publica tu rama y solicita integración hacia `01-monolito`.
