# Estado de la segunda entrega · 14 de noviembre de 2026

## Ramas y entregas integradas

Se conservan tres ramas permanentes: `main`, `01-monolito` (entrega terminada) y `02-separacion` (segunda entrega). Las ramas `trabajo/*` de la ronda anterior se eliminaron después de integrar sus commits. Para una corrección nueva, partir de `02-separacion`, abrir PR hacia esa rama y borrar la rama temporal tras el merge.

| Responsable | Entrega | Estado |
|---|---|---|
| Oscar | [PR #4](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/4): reportes de hallazgo, filtros y outbox HTTP | Integrado en `02-separacion` |
| Luisa | [PR #5](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/5): servicio de alertas | El PR se fusionó en `main`; se incorporó su commit a `02-separacion` y se completó Compose, el worker y el contrato de bandeja durante la integración |
| Ceci | [PR #7](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/7): usuarios y JWT | Integrado en `02-separacion` |
| Amy | [PR #8](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/8): interfaz con JWT, hallazgos, suscripciones y bandeja | Integrado en `02-separacion` |

## Qué funciona hoy

- Traefik atiende `localhost:8000` y balancea las peticiones entre `reportes_a` y `reportes_b`. También enruta `/api/alertas` al proceso de alertas. El puerto 8001 publicado por Traefik es una compatibilidad temporal para la web anterior; la tarea de Amy lo elimina. Identidad todavía reside con reportes; la separación es tarea de Ceci.
- PostgreSQL conserva `four_nodes`; un contenedor de inicialización crea `four_nodes_alerts` solo si falta. El volumen de `01-monolito` no se borra.
- Publicar un extravío o hallazgo guarda su evento de outbox en la misma transacción. El trabajador consulta el feed cada 10 segundos, crea alertas para quienes ya seguían el municipio y confirma el evento después de guardar sus alertas. Una restricción única evita alertas duplicadas en los reintentos.
- La API de bandeja devuelve `type` y `public_url` conforme al contrato. El proceso `app` ya no monta rutas de alertas ni crea sus tablas en `four_nodes`.

## Verificación realizada

1. En `01-monolito`, `docker compose run --rm app sh -c "pip install -q '.[dev]' && pytest -q"`: **10 pruebas aprobadas**.
2. En `02-separacion`, `docker compose up --build -d`: arranque correcto de `db`, inicializadores, dos réplicas de reportes, `alertas` y Traefik; `/health/ready` responde 200.
3. Antes de Traefik, la suite tuvo **34 pruebas aprobadas**; tras integrar a Amy y el gateway pasó **36 pruebas**.
4. `python3 scripts/smoke_02.py`: registró dos cuentas, publicó un hallazgo idempotente, entregó una alerta por HTTP a la cuenta suscrita y confirmó que la bandeja de la otra cuenta seguía vacía. La alerta llegó en menos de 9 segundos en esta ejecución local.
5. Se detuvo solo `alertas`, se publicó otro hallazgo con respuesta 201 y se consultó públicamente. Al reiniciar `alertas`, la bandeja de la cuenta suscrita recibió una sola alerta. El ensayo conservó las bases y los contenedores de `app` y PostgreSQL.
6. Tras integrar el PR #8, la suite completa pasó **36 pruebas Python**. La prueba de navegador de Amy pasó en Chrome con APIs simuladas, incluidos los anchos 390, 768 y 1440 px.
7. Con Chrome, Docker y PostgreSQL reales, dos cuentas independientes se registraron, una siguió un municipio y la otra publicó un hallazgo y un extravío. Las dos páginas públicas abrieron y ambas alertas aparecieron en la bandeja del suscriptor, sin errores JavaScript.
8. En una medición local por HTTP con 20 cuentas suscritas, la publicación respondió en 0.01 s y las **20 alertas** aparecieron en **5.55 s** desde la respuesta. Es un ensayo, todavía sin script reproducible ni repetición estadística.
9. `python3 scripts/verify_gateway.py`: observó las dos réplicas, comprobó que el feed interno devuelve 404 desde el puerto público, detuvo `reportes_a` y completó `scripts/smoke_02.py` con `reportes_b`; luego reinició la primera. Traefik necesitó unos segundos para detectar la caída, por lo que puede responder 502 durante ese intervalo.

El navegador de Amy se verificó con tres anchos, pero falta una revisión manual de accesibilidad y de los recorridos completos en teléfono real. Estas pruebas locales no demuestran despliegue público ni disponibilidad ante caída de PostgreSQL.

## Lo que falta y quién lo hace

La versión `02-separacion` cumple los flujos básicos de reportes y alertas. La API de mascotas permite crear y consultar fichas, pero la web no permite registrar una por separado ni elegir una guardada para publicar; tampoco existe edición de ficha propia, aunque el PRD la menciona. El proyecto final todavía debe cerrar esos detalles y los compromisos adicionales del PRD y la [rúbrica](../RUBRICA.md): PDF, pitch, identidad separada y pruebas reproducibles de fallas y tiempos. El [plan de cierre](PLAN_CIERRE_RUBRICA.md) asigna cada tarea. Esta rama aún no se incorpora a `main` como versión final.

## Cómo continuar

1. `git fetch origin` y `git switch 02-separacion`; actualizar con `git pull --ff-only`.
2. `python3 scripts/setup_env.py` crea las claves faltantes sin cambiar las ya usadas por un volumen existente.
3. `docker compose up --build -d`; abrir `http://localhost:8000/docs`.
4. Ejecutar `python3 scripts/smoke_02.py` y `python3 scripts/verify_gateway.py`. Crean cuentas y reportes de prueba en la base local. Para detener sin borrar datos: `docker compose down`.
