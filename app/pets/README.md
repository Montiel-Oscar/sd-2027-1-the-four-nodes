# Luisa · mascotas

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/luisa-mascotas`. En GitHub Desktop, selecciona la rama base, actualízala y crea tu rama personal.

Implementa el modelo y las rutas de mascotas en esta carpeta. El dueño se obtiene con `Depends(get_actor_id)` de `app/core/auth.py`. Acuerda con Oscar la función `create_pet_for_owner(session, owner_id, *, name, species, traits)` descrita en [los contratos](../../docs/CONTRATOS_01_MONOLITO.md): **no hace commit**, para que Oscar pueda guardar mascota y reporte en una sola transacción.

**Entregable:** registrar, listar y consultar mascotas propias; prueba de propiedad y de creación reutilizable dentro de otra transacción. No edites el modelo de reportes. Publica tu rama y solicita integración hacia `01-monolito`.
