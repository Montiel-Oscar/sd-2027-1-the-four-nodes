# Resultados finales de mascotas, tiempos y resiliencia · Luisa M. Segura Cedeño

**Rama de trabajo:** `trabajo/luisa-evidencia-final` (sobre `02-separacion`)  
**Fecha:** noviembre de 2026

---

## 1. Edición de ficha propia y conservación de reportes publicados

- **Implementación:** `PUT /api/mascotas/{pet_id}` (`app/pets/router.py`) y `update_pet_for_owner` (`app/pets/service.py`) actualizan `name`, `species` y `traits` únicamente cuando `Pet.id == pet_id` y `Pet.owner_id == actor_id`. Si la mascota no existe o pertenece a otro usuario, se responde `404` sin modificar registros ajenos.
- **Pruebas automatizadas (`tests/test_pets.py`):**
  - Creación, listado, consulta y edición de ficha propia.
  - Rechazo (`404`) al intentar consultar o editar la ficha de otro dueño.
- **Conservación en reportes publicados:** al publicar un extravío, los datos descriptivos del reporte quedan registrados en el reporte y no se sobreescriben retroactivamente si el dueño edita su ficha posteriormente.

---

## 2. Decisión arquitectónica: Outbox transaccional y ACK frente a aviso síncrono

- **Decisión:** registrar el evento en la tabla `outbox` dentro de la misma transacción local de `reportes` al confirmar el reporte, y que el servicio `alertas` consuma eventos y envíe `ACK` (`POST .../internal/events/{event_id}/ack`) **después** de persistir las alertas de forma idempotente (`event_id`, `recipient_id`).
- **Alternativas descartadas:**
  1. *Enviar alertas de forma síncrona dentro del `POST` de publicación:* acoplaba la latencia y disponibilidad de `alertas` y de todos los destinatarios a la respuesta HTTP del reporte; si `alertas` fallaba o tardaba, la publicación corría riesgo de fallar o bloquearse.
  2. *Enviar `ACK` antes de confirmar las alertas en la BD de `alertas`:* si el proceso de `alertas` caía tras el `ACK` y antes del `commit`, el evento se perdería sin reintento.

---

## 3. Comandos reproducibles de tiempos y fallas

Con `docker compose up --build -d` en ejecución (sin borrar volúmenes):

```bash
# 3 repeticiones con 20 suscriptores (hallazgos y extravíos)
python3 scripts/resilience_20_subscribers.py --subscribers 20 --trials 3 --timeout 150

# Incluye pruebas de caída de `alertas` y caída de `postgres`
python3 scripts/resilience_20_subscribers.py --subscribers 20 --trials 3 --timeout 150 --with-faults
cat << 'EOF' > docs/RESULTADOS_FINALES.md
# Resultados finales de mascotas, tiempos y resiliencia · Luisa M. Segura Cedeño

**Rama de trabajo:** `trabajo/luisa-evidencia-final` (sobre `02-separacion`)  
**Fecha:** noviembre de 2026

---

## 1. Edición de ficha propia y conservación de reportes publicados

- **Implementación:** `PUT /api/mascotas/{pet_id}` (`app/pets/router.py`) y `update_pet_for_owner` (`app/pets/service.py`) actualizan `name`, `species` y `traits` únicamente cuando `Pet.id == pet_id` y `Pet.owner_id == actor_id`. Si la mascota no existe o pertenece a otro usuario, se responde `404` sin modificar registros ajenos.
- **Pruebas automatizadas (`tests/test_pets.py`):**
  - Creación, listado, consulta y edición de ficha propia.
  - Rechazo (`404`) al intentar consultar o editar la ficha de otro dueño.
- **Conservación en reportes publicados:** al publicar un extravío, los datos descriptivos del reporte quedan registrados en el reporte y no se sobreescriben retroactivamente si el dueño edita su ficha posteriormente.

---

## 2. Decisión arquitectónica: Outbox transaccional y ACK frente a aviso síncrono

- **Decisión:** registrar el evento en la tabla `outbox` dentro de la misma transacción local de `reportes` al confirmar el reporte, y que el servicio `alertas` consuma eventos y envíe `ACK` (`POST .../internal/events/{event_id}/ack`) **después** de persistir las alertas de forma idempotente (`event_id`, `recipient_id`).
- **Alternativas descartadas:**
  1. *Enviar alertas de forma síncrona dentro del `POST` de publicación:* acoplaba la latencia y disponibilidad de `alertas` y de todos los destinatarios a la respuesta HTTP del reporte; si `alertas` fallaba o tardaba, la publicación corría riesgo de fallar o bloquearse.
  2. *Enviar `ACK` antes de confirmar las alertas en la BD de `alertas`:* si el proceso de `alertas` caía tras el `ACK` y antes del `commit`, el evento se perdería sin reintento.

---

## 3. Comandos reproducibles de tiempos y fallas

Con `docker compose up --build -d` en ejecución (sin borrar volúmenes):

```bash
# 3 repeticiones con 20 suscriptores (hallazgos y extravíos)
python3 scripts/resilience_20_subscribers.py --subscribers
