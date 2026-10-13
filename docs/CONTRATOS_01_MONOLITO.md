# Contratos comunes de `01-monolito`

Este acuerdo permite editar módulos distintos sin bloquearse. Si hay que cambiarlo, avisen al equipo antes de modificar dos módulos a la vez.

## Identidad y base

- Toda clave primaria es un UUID. La cuenta de demostración tiene el ID fijo de `app/core/auth.py`; todos los módulos obtienen el actor mediante `get_actor_id`, nunca copiando el UUID.
- Los modelos SQLAlchemy heredan de `app.core.db.Base`. Los modelos de cada módulo viven en su propio `models.py`; las tablas comparten **una sola** base PostgreSQL en esta rama. Eviten relaciones ORM entre módulos: basta guardar el UUID relacionado.
- Una función que participa en la publicación recibe la **misma sesión** de base de datos; no hace `commit` por su cuenta. El endpoint de reportes decide confirmar o revertir toda la operación.

## Mascotas: Luisa ↔ Oscar

`app.pets.service.create_pet_for_owner(session, owner_id, *, name, species, traits)` devuelve la mascota creada sin confirmar la transacción. `get_pet_for_owner(session, owner_id, pet_id)` devuelve la mascota o indica que no pertenece al dueño. Luisa documenta cualquier validación adicional en su carpeta.

Rutas iniciales: `POST /api/mascotas`, `GET /api/mascotas` y `GET /api/mascotas/{id}`. El cuerpo mínimo es `{ "name": "Luna", "species": "perro", "traits": "pelaje café" }`.

## Extravíos: Oscar ↔ Amy

`POST /api/reportes/extravios` requiere la cabecera `Idempotency-Key` y **uno** de estos datos: `pet_id` de una ficha propia o `pet` con `name`, `species` y `traits`. Los demás campos son `seen_at` (fecha/hora ISO 8601), `municipality`, `neighborhood`, `landmark`, y opcionalmente `public_phone` junto con `show_phone: true`. Si `show_phone` no es verdadero, el teléfono no aparece en la respuesta pública.

Respuesta exitosa: HTTP `201` con `id`, `public_url` y campos públicos. El mismo usuario y la misma clave de idempotencia devuelven el mismo ID sin crear otro reporte; una clave reutilizada con datos distintos es un error de conflicto. `GET /api/reportes/extravios/{id}` es público y devuelve solo datos públicos. Los nombres de campo se mantienen en inglés para que el contrato de API sea uniforme; los textos de interfaz van en español.

Oscar guarda el reporte y un evento pendiente en una sola transacción. El evento contiene como mínimo `id`, `report_id`, `type`, `municipality`, `created_at` y `processed_at` opcional. No se envía todavía a otro proceso: la extracción de alertas corresponde a `02-separacion`.

## Interfaz: Amy ↔ el resto

El formulario utiliza exactamente el contrato de extravíos, genera una clave nueva por intento de publicación y la conserva si reintenta tras un fallo de red. La página del reporte usa `GET /api/reportes/extravios/{id}`. La pantalla inicial puede mostrar el formulario y un enlace a la documentación de la API. No se requiere mapa ni carga de fotos.

## Criterio de integración

Con `docker compose up --build`: `/health/ready` responde; se crea una mascota junto con el extravío; el enlace público carga el reporte; al repetir la solicitud con la misma clave se obtiene el mismo ID; al reiniciar los contenedores el reporte sigue disponible. El equipo documenta en cada carpeta lo que implementó y cómo lo verificó.
