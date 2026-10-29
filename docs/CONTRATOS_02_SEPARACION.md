# Contratos fijos · `02-separacion`

Los JSON usan campos en inglés; la interfaz muestra textos en español. Los ID son UUID y las fechas se envían como ISO 8601 con zona horaria. Un error de validación devuelve 422; un recurso ausente devuelve 404. No cambien rutas, nombres de campo o códigos de éxito sin avisar a los otros tres integrantes.

## Identidad: Ceci ↔ Oscar, Luisa y Amy

`POST /api/usuarios/register` recibe `{ "email": "persona@example.org", "password": "una-clave-de-8-o-mas" }`, crea un usuario y devuelve `201 { "id": "uuid", "email": "persona@example.org" }`. Correo duplicado: 409. Se normaliza a minúsculas; nunca se devuelve el hash.

`POST /api/usuarios/login` recibe el mismo cuerpo y devuelve `200 { "access_token": "...", "token_type": "bearer" }`. Credenciales incorrectas: 401. `GET /api/usuarios/me` devuelve `200 { "id": "uuid", "email": "..." }` con Bearer válido. Las claves se guardan con Argon2id y nunca en texto claro.

`app.core.auth.get_actor_id` conserva su nombre y devuelve `UUID` a las rutas privadas. Lee `Authorization: Bearer <token>`, verifica localmente firma HS256, `sub`, emisor `the-four-nodes` y vencimiento de 60 minutos usando `AUTH_SECRET`; no consulta identidad en cada petición. Falta o invalidez: 401. `app` y `alertas` reciben el **mismo** secreto por entorno; nunca se sube el valor real. Las pruebas pueden sustituir esta dependencia. En esta rama identidad sigue dentro del proceso `app` y su base.

## Reportes públicos: Oscar ↔ Amy

El `POST /api/reportes/extravios` existente conserva su contrato, con Bearer obligatorio. `GET /api/reportes/extravios/{id}` sigue público. Se añade `GET /api/reportes/extravios?municipality=Coyoacán` que devuelve una lista de objetos públicos, del más reciente al más antiguo, máximo 100. Sin filtro devuelve los 100 más recientes.

`POST /api/reportes/hallazgos` requiere Bearer e `Idempotency-Key`. Cuerpo mínimo:

```json
{
  "description": "Perro mediano con collar rojo",
  "seen_at": "2026-10-27T17:00:00-06:00",
  "municipality": "Coyoacán",
  "neighborhood": "Del Carmen",
  "landmark": "Cerca del parque",
  "show_phone": false
}
```

`public_phone` es opcional y solo se conserva/publica si `show_phone` es verdadero. Respuesta 201: `id`, `public_url`, `description`, `seen_at`, `municipality`, `neighborhood`, `landmark`, `public_phone`, `created_at`. `public_url` apunta a `/reportes/hallazgos/{id}`. Repetir usuario + clave + cuerpo devuelve mismo ID; clave con otro cuerpo, 409. `GET /api/reportes/hallazgos/{id}` es público. `GET /api/reportes/hallazgos?municipality=...` devuelve lista pública, máximo 100. Una persona puede publicar hallazgo sin asociarlo a una ficha o extravío.

## Eventos internos: Oscar ↔ Luisa

Solo el proceso de alertas usa estas rutas en `app:8000`. Ambas exigen `X-Internal-Token` igual a `INTERNAL_API_TOKEN` (comparación segura); si el secreto no está configurado, fallan cerradas. No usan el Bearer de un usuario.

`GET /api/reportes/internal/events?limit=50` devuelve `200 { "events": [...] }`, ordenados del más antiguo al más reciente, solo con `processed_at = null`. `limit` admite 1 a 50. Cada elemento contiene exactamente estos campos públicos del evento:

```json
{
  "id": "uuid-del-evento",
  "report_id": "uuid-del-reporte",
  "type": "missing_pet.reported",
  "municipality": "Coyoacán",
  "created_at": "2026-10-27T23:00:00Z",
  "public_url": "/reportes/extravios/uuid-del-reporte"
}
```

`type` también puede ser `found_pet.reported`, con URL `/reportes/hallazgos/{id}`. La URL es **ruta relativa**; Amy forma el enlace con el origen de la web. La fecha de corte para suscriptores es `created_at` del evento. El feed incluye eventos antiguos pendientes de `pending_report_events` y eventos nuevos de `outbox_events_v1`.

`POST /api/reportes/internal/events/{event_id}/ack` devuelve 204 y fija `processed_at` si estaba vacío. Repetir el ACK devuelve 204; ID inexistente, 404. El trabajador llama a ACK **solo después** de confirmar sus alertas. Publicar jamás llama a este endpoint ni a alertas.

## Alertas: Luisa ↔ Amy

Servicio separado en `localhost:8001`; las rutas privadas requieren el mismo Bearer. `POST /api/alertas/subscriptions` recibe `{ "municipality": "Coyoacán" }` y devuelve 201 con `{ "id": "uuid", "municipality": "Coyoacán", "created_at": "ISO" }`; repetir la misma suscripción del usuario no crea otra. `GET /api/alertas/subscriptions` devuelve su lista. `DELETE /api/alertas/subscriptions/{id}` devuelve 204 solo para la suscripción propia.

`GET /api/alertas/inbox` devuelve una lista, del más reciente al más antiguo, máximo 100:

```json
[{ "id": "uuid", "event_id": "uuid", "type": "missing_pet.reported", "municipality": "Coyoacán", "public_url": "/reportes/extravios/uuid", "created_at": "ISO" }]
```

La tabla de alertas exige único `(event_id, recipient_id)`. Solo se crea alerta para quien ya seguía ese municipio cuando se creó el evento (`subscription.created_at <= event.created_at`). `GET /health/live` y `/health/ready` del servicio verifican proceso y base propia. El trabajador consulta el feed cada 10 s con timeout de 2 s y procesa a lo sumo 50 eventos por lote. Al caer reportes, reintenta después; al caer alertas, los reportes siguen guardándose.

## Web: Amy ↔ todas las APIs

La web carga en `localhost:8000`, envía Bearer en publicaciones y suscripciones, y llama a alertas en `localhost:8001` (CORS limitado a `http://localhost:8000`). Guardar el token en `sessionStorage` basta para la demo local. En fallo de red, conservar cuerpo y `Idempotency-Key`; cambiar el cuerpo inicia una clave nueva. La bandeja abierta se consulta cada 30 s o menos. El formulario exige consentimiento antes de mostrar teléfono y pide una referencia pública, no domicilio particular.
