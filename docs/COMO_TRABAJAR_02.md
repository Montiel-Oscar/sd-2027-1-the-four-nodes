# Instrucciones de Git y ejecución · versión 1

## Para las cuatro personas

1. Clona el repositorio o haz **Fetch origin** en GitHub Desktop. Selecciona `02-separacion` como rama base y haz **Pull origin**. No partas de `main` ni de `01-monolito`.
2. Crea **tu** rama indicada en [el plan](PLAN_02_SEPARACION.md). En terminal: `git switch 02-separacion`, `git pull --ff-only origin 02-separacion`, `git switch -c trabajo/TU-RAMA`. En GitHub Desktop: **Current branch → 02-separacion → New branch**.
3. Lee [los contratos](CONTRATOS_02_SEPARACION.md) antes de editar. Trabaja principalmente en tu carpeta y añade pruebas de comportamiento y fallas. No subas `.env`, tokens, contraseñas, bases de datos ni archivos temporales. El autor de tus commits debe ser tu propia cuenta.
4. Haz commit, publica tu rama y abre un Pull Request **base: `02-separacion`**. Incluye qué cambió, cómo se prueba y qué dependencias de otras ramas permanecen. No marques como completo un flujo que solo funciona con datos simulados.
5. Antes del merge, trae los cambios recientes de `02-separacion` a tu rama y resuelve conflictos. Una persona integra por vez. Después de cada merge, todos hacen Fetch/Pull de `02-separacion`.

## Preparar el entorno local

En `02-separacion`, copia `.env.example` a `.env`. Conserva las variables existentes y agrega `AUTH_SECRET` e `INTERNAL_API_TOKEN` con valores aleatorios distintos, por ejemplo generados con `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`. El archivo `.env` está ignorado por Git. Luisa documentará las variables adicionales de la base de alertas en su PR.

Mientras se integran las ramas, la base puede seguir levantando el monolito anterior. Tras integrar la etapa, `docker compose up --build -d` debe dejar `app` en `http://localhost:8000` y `alertas` en `http://localhost:8001`. `docker compose ps` debe mostrar ambos saludables; `docker compose logs app alertas` ayuda a diagnosticar. Para detener sin borrar datos: `docker compose down`. **No uses `down -v`** sobre una base con datos que quieras conservar.

Para pruebas Python dentro del contenedor: `docker compose exec app pip install '.[dev]'` y `docker compose exec app pytest -q`. Luisa añadirá el comando de pruebas del proceso de alertas; si usa la misma imagen, el código y dependencias estarán disponibles allí. Prueba los cambios de API con `/docs` y repite las solicitudes con la misma clave de idempotencia.

## Prueba manual de la frontera distribuida

1. Registra/inicia sesión con dos cuentas y guarda el token de cada una. Suscribe la segunda cuenta a un municipio desde la web.
2. Publica un extravío con la primera. Comprueba que aparece en su enlace público y que la bandeja de la segunda recibe exactamente una alerta.
3. Detén solo alertas: `docker compose stop alertas`. Publica otro extravío y un hallazgo; ambos deben responder 201 y seguir visibles.
4. Reinicia alertas: `docker compose start alertas`. Comprueba que recupera los eventos pendientes y que cada destinatario recibe una sola alerta por evento. Repite el ACK o reinicia el trabajador para comprobar deduplicación.
5. Reinicia `app`, `alertas` y PostgreSQL sin borrar volúmenes; comprueba persistencia. Registra tiempos desde `created_at` del evento hasta alerta guardada y hasta que aparece en la bandeja web.

## Archivos que cada quien debe leer primero

- Oscar: `app/reports/models.py`, `service.py`, `router.py`, `tests/test_reports.py` y [contrato de eventos](CONTRATOS_02_SEPARACION.md#eventos-internos-oscar--luisa).
- Luisa: `app/alerts/`, `app/main.py`, `app/core/db.py`, `compose.yaml` y los contratos de eventos/alertas. Su base no debe compartir metadata ORM con reportes.
- Ceci: `app/identity/`, `app/core/auth.py`, `app/core/db.py` y contrato de identidad. Sus pruebas deben demostrar 401 y propiedad por usuario.
- Amy: `app/web/static/`, `app/web/router.py` y contratos de identidad, hallazgos y bandeja. Conserva accesible el flujo actual de extravíos.
