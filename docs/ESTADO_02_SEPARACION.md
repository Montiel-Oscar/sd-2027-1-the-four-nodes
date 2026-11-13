# Estado de la segunda entrega · 13 de noviembre de 2026

## Ramas y entregas integradas

Se conservan tres ramas permanentes: `main`, `01-monolito` (entrega terminada) y `02-separacion` (segunda entrega). Las ramas `trabajo/*` de la ronda anterior se eliminaron después de integrar sus commits. Para una corrección nueva, partir de `02-separacion`, abrir PR hacia esa rama y borrar la rama temporal tras el merge.

| Responsable | Entrega | Estado |
|---|---|---|
| Oscar | [PR #4](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/4): reportes de hallazgo, filtros y outbox HTTP | Integrado en `02-separacion` |
| Luisa | [PR #5](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/5): servicio de alertas | El PR se fusionó en `main`; se incorporó su commit a `02-separacion` y se completó Compose, el worker y el contrato de bandeja durante la integración |
| Ceci | [PR #7](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/7): usuarios y JWT | Integrado en `02-separacion` |
| Amy | [PR #8](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/8): interfaz con JWT, hallazgos, suscripciones y bandeja | Integrado en `02-separacion` |

## Qué funciona hoy

- `app` atiende identidad, mascotas y reportes en el puerto 8000. `alertas` atiende suscripciones y bandeja en el 8001. Ambos verifican el mismo JWT sin compartir el acceso a la tabla de usuarios.
- PostgreSQL conserva `four_nodes`; un contenedor de inicialización crea `four_nodes_alerts` solo si falta. El volumen de `01-monolito` no se borra.
- Publicar un extravío o hallazgo guarda su evento de outbox en la misma transacción. El trabajador consulta el feed cada 10 segundos, crea alertas para quienes ya seguían el municipio y confirma el evento después de guardar sus alertas. Una restricción única evita alertas duplicadas en los reintentos.
- La API de bandeja devuelve `type` y `public_url` conforme al contrato. El proceso `app` ya no monta rutas de alertas ni crea sus tablas en `four_nodes`.

## Verificación realizada

1. En `01-monolito`, `docker compose run --rm app sh -c "pip install -q '.[dev]' && pytest -q"`: **10 pruebas aprobadas**.
2. En `02-separacion`, `docker compose up --build -d`: arranque correcto de `db`, `app`, inicializador y `alertas`; ambos `/health/ready` respondieron 200.
3. En `02-separacion`, el mismo comando de `pytest`: **34 pruebas aprobadas**.
4. `python3 scripts/smoke_02.py`: registró dos cuentas, publicó un hallazgo idempotente, entregó una alerta por HTTP a la cuenta suscrita y confirmó que la bandeja de la otra cuenta seguía vacía. La alerta llegó en menos de 9 segundos en esta ejecución local.
5. Se detuvo solo `alertas`, se publicó otro hallazgo con respuesta 201 y se consultó públicamente. Al reiniciar `alertas`, la bandeja de la cuenta suscrita recibió una sola alerta. El ensayo conservó las bases y los contenedores de `app` y PostgreSQL.
6. Tras integrar el PR #8, la suite completa pasó **36 pruebas Python**. La prueba de navegador de Amy pasó en Chrome con APIs simuladas, incluidos los anchos 390, 768 y 1440 px.
7. Con Chrome, Docker y PostgreSQL reales, dos cuentas independientes se registraron, una siguió un municipio y la otra publicó un hallazgo y un extravío. Las dos páginas públicas abrieron y ambas alertas aparecieron en la bandeja del suscriptor, sin errores JavaScript.
8. En una medición local por HTTP con 20 cuentas suscritas, la publicación respondió en 0.01 s y las **20 alertas** aparecieron en **5.55 s** desde la respuesta. Es un ensayo, todavía sin script reproducible ni repetición estadística.

El navegador de Amy se verificó con tres anchos, pero falta una revisión manual de accesibilidad y de los recorridos completos en teléfono real. Estas pruebas locales no demuestran despliegue público ni disponibilidad ante caída de PostgreSQL.

## Lo que falta y quién lo hace

La versión `02-separacion` cumple sus cuatro flujos básicos. El proyecto final todavía debe cerrar los compromisos adicionales del PRD y los entregables de la [rúbrica](../RUBRICA.md): PDF, pitch, identidad separada, gateway, dos réplicas de reportes y pruebas reproducibles de fallas. El [plan de cierre](PLAN_CIERRE_RUBRICA.md) asigna cada tarea. Esta rama aún no se incorpora a `main` como versión final.

## Cómo continuar

1. `git fetch origin` y `git switch 02-separacion`; actualizar con `git pull --ff-only`.
2. Copiar `.env.example` a `.env` si falta. Generar dos valores distintos con `python3 -c 'import secrets; print(secrets.token_hex(32))'` y colocarlos en `AUTH_SECRET` e `INTERNAL_API_TOKEN`. `POSTGRES_PASSWORD` también debe estar definido.
3. `docker compose up --build -d`; abrir `http://localhost:8000/docs` y `http://localhost:8001/docs`.
4. Ejecutar `python3 scripts/smoke_02.py`. Crea dos cuentas de prueba y un hallazgo en la base local. Para detener sin borrar datos: `docker compose down`.
