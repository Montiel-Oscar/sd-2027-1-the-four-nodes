# Oscar · extravíos (tarea 1)

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/oscar-extravios`. En GitHub Desktop, elige `01-monolito` en **Current branch**, actualízala y crea la nueva rama desde ella.

Implementa en esta carpeta el reporte de extravío, la consulta pública y el evento pendiente. Sigue el cuerpo y la respuesta de [los contratos](../../docs/CONTRATOS_01_MONOLITO.md). Para crear una mascota nueva, llama a la función de Luisa usando **la misma sesión** de SQLAlchemy. El reporte y el evento se confirman juntos; si cualquier paso falla, se revierten juntos.

**Entregable:** `POST /api/reportes/extravios` y `GET /api/reportes/extravios/{id}`; clave de idempotencia por usuario; prueba de publicación y prueba de reintento sin duplicado. El enlace público debe incluir el ID guardado. No implementes todavía la comunicación con un servicio de alertas separado.

## Implementación de Oscar

- `POST /api/reportes/extravios` acepta `pet` para crear una ficha o `pet_id` para reutilizar una propia. Requiere `Idempotency-Key` y responde `201` con el reporte y `public_url`.
- `GET /api/reportes/extravios/{id}` permite consultar los datos sin iniciar sesión. `public_url` apunta a la página pública de Amy en `/reportes/extravios/{id}`.
- El reporte conserva una copia de nombre, especie y rasgos para que cambios posteriores a la ficha no alteren lo publicado.
- El reporte y un evento `missing_pet.reported` se guardan juntos. El evento empieza con `processed_at = null`; la entrega a alertas se implementará en `02-separacion`.
- La clave de idempotencia es única por usuario. Repetir el mismo cuerpo devuelve el mismo ID; reutilizar la clave con otros datos devuelve `409`. Una solicitud simultánea que pierde la carrera por la clave revierte su mascota nueva y devuelve el reporte que ganó.
- `public_phone` solo se almacena y devuelve si `show_phone` es verdadero.

Ejemplo después de integrar `app/pets/service.py` de Luisa:

```bash
curl -i http://localhost:8000/api/reportes/extravios \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: luna-2026-10-13-1' \
  -d '{"pet":{"name":"Luna","species":"perro","traits":"pelaje café"},"seen_at":"2026-10-12T18:00:00-06:00","municipality":"Coyoacán","neighborhood":"Del Carmen","landmark":"Cerca del parque"}'
```

Para ejecutar las pruebas de este módulo: `docker compose exec app pip install '.[dev]'` y después `docker compose exec app pytest -q tests/test_reports.py`. Las pruebas sustituyen la función de Luisa por una implementación de prueba con el mismo contrato; comprueban publicación, reintento, privacidad, propiedad y reversión de la transacción.

**Integración pendiente:** Luisa agrega `create_pet_for_owner` y `get_pet_for_owner` en `app/pets/service.py`. Deben recibir la sesión existente, devolver `id`, `name`, `species` y `traits`, y no hacer `commit`. Con su rama integrada, repetir el ejemplo anterior con PostgreSQL y comprobar que el enlace público sigue disponible tras reiniciar los contenedores.

Haz commits con tu identidad de Git, publica `trabajo/oscar-extravios` y solicita integración hacia `01-monolito`. Después de integrar identidad y mascotas, coordina una prueba del flujo completo con Amy.

## Versión 1 distribuida · trabajo de Oscar

La rama `trabajo/oscar-reportes-v1` parte de `02-separacion`. Mantiene los endpoints de extravíos y añade:

- `POST /api/reportes/hallazgos`, `GET /api/reportes/hallazgos/{id}` y `GET /api/reportes/hallazgos?municipality=...`.
- `GET /api/reportes/extravios?municipality=...` para explorar reportes públicos.
- Una tabla `outbox_events_v1` genérica para los nuevos eventos de extravío y hallazgo, guardados en la misma transacción que el reporte. La tabla `pending_report_events` de la etapa anterior se mantiene para ofrecer sus eventos pendientes sin borrar ni migrar el volumen.
- `GET /api/reportes/internal/events?limit=50` y `POST /api/reportes/internal/events/{id}/ack`, protegidos con `X-Internal-Token`. Este token debe coincidir con `INTERNAL_API_TOKEN` en el entorno de `app` y del trabajador de Luisa. Sin configurar el secreto, la API interna responde 503; con token incorrecto, 403.

El feed devuelve eventos pendientes antiguos y nuevos, ordenados por fecha. El ACK es repetible y fija `processed_at` sin borrar el evento. **Publicar nunca llama a alertas**: el proceso de Luisa consultará este feed, guardará alertas en su propia base y después llamará al ACK. El contrato exacto está en [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md).

Las pruebas del módulo están en `tests/test_reports.py`: `docker compose exec app pytest -q tests/test_reports.py`. Se comprobó además hallazgo, reintento, feed y ACK contra PostgreSQL. El enlace HTML `/reportes/hallazgos/{id}` quedará disponible cuando Amy integre la vista pública; mientras tanto los datos públicos se consultan en `/api/reportes/hallazgos/{id}`. Cuando Ceci integre Bearer, las pruebas existentes deben sustituir `get_actor_id` por una dependencia de prueba.

Para la integración, Luisa debe configurar el mismo token interno en `app` y `alertas` desde `.env`, y consumir el JSON del feed sin compartir tablas. Tras integrar su PR, probar el escenario `docker compose stop alertas` → publicar → `docker compose start alertas` → una sola alerta por destinatario.
