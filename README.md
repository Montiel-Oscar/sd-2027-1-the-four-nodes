# The Four Nodes · búsqueda comunitaria de mascotas

Proyecto final de Sistemas Distribuidos 2027-1 de la FI-UNAM. Una persona publica el extravío de su mascota y comparte el enlace del reporte; otras personas pueden registrar hallazgos y seguir un municipio para recibir alertas. El alcance y las decisiones están en [docs/PRD.md](docs/PRD.md).

## Equipo

1. **Oscar Ivan Montiel Juarez** — [@Montiel-Oscar](https://github.com/Montiel-Oscar)
2. **Luisa María Segura Cedeño** — [@LuisaCedeno](https://github.com/LuisaCedeno)
3. **Cecilia Ximena Solis Cisneros** — [@CeciliaXimenaSolisCisneros](https://github.com/CeciliaXimenaSolisCisneros)
4. **Amy Valentina Veraza García** — [@Amyv19](https://github.com/Amyv19)

## Primera entrega: `01-monolito`

La rama `main` conserva la versión estable y la documentación. La rama `01-monolito` guarda la primera entrega: una aplicación FastAPI y una base PostgreSQL levantadas con Docker Compose. Su flujo principal permite **publicar un extravío**, capturando o seleccionando la mascota y obteniendo un enlace público. El monolito usa una cuenta de demostración; la separación en servicios avanza en `02-separacion`.

**Entrega del curso:** sábado 17 de octubre de 2026, antes de las 07:00. El equipo comparte la liga del repositorio en su comentario de la Discussion #44 cuando la rama `01-monolito` tenga el flujo principal funcionando.

La [guía de colaboración](docs/COMO_COLABORAR.md) explica cómo entrar a la rama, crear una rama personal y entregar cambios con GitHub Desktop o Git. El [reparto de tareas](docs/REPARTO_01_MONOLITO.md) indica qué hará cada integrante y cómo integrar el trabajo.

## Estado del monolito · 5 de noviembre de 2026

La rama `01-monolito` integra mascotas, reportes, una cuenta de demostración y una interfaz web. Se puede publicar un extravío con una mascota nueva, reintentar sin duplicarlo y abrir su página pública. El reporte y el evento pendiente se guardan en una sola transacción. También se pueden registrar y consultar fichas propias de mascotas.

Luisa entregó mascotas en la [solicitud #2](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/2), Amy la interfaz en la [#3](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/3), Oscar reportes en la [#1](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/1) y Ceci verificó la identidad de demostración en la [#6](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/6). La rama `01-monolito` pasó 10 pruebas el 5 de noviembre de 2026.

## Levantar la aplicación

En la rama `01-monolito`, con Docker y Docker Compose instalados:

```bash
cp .env.example .env
docker compose up --build
```

Abrir `http://localhost:8000/` para la página inicial, `http://localhost:8000/docs` para la API y `http://localhost:8000/health/ready` para comprobar la conexión con PostgreSQL. El archivo `.env` es local y no se sube a GitHub. Para detener la aplicación, usar `Ctrl+C` y después `docker compose down`; el volumen de la base conserva los datos.

## Ramas del proyecto

Las tres ramas permanentes son `main` (referencia del proyecto), `01-monolito` (primera entrega terminada) y `02-separacion` (segunda entrega en integración). Las ramas personales son temporales: parten de su rama de etapa y se borran después de integrar el PR. Las etapas posteriores del PRD todavía no tienen rama.

## Primera versión distribuida: `02-separacion`

El [plan de cuatro tareas](docs/PLAN_02_SEPARACION.md) y los [contratos](docs/CONTRATOS_02_SEPARACION.md) siguen vigentes. El [estado detallado](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/blob/02-separacion/docs/ESTADO_02_SEPARACION.md) vive en `02-separacion`.

La [rúbrica final](RUBRICA.md) y el [nuevo reparto de cierre](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/blob/02-separacion/docs/PLAN_CIERRE_RUBRICA.md) fijan los pendientes para la entrega del **28 de noviembre antes de las 07:00** (hora de Ciudad de México).

### Lista de avance

- [x] **Oscar:** reportes de hallazgo, listas y outbox HTTP ([PR #4](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/4)).
- [x] **Ceci:** registro, login y JWT compartido ([PR #7](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/7)).
- [x] **Luisa + integración:** servicio de alertas, segunda base lógica y Compose ([PR #5](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/5)); su PR se fusionó originalmente en `main`, y el trabajo se incorporó también a `02-separacion`.
- [x] **Amy:** interfaz distribuida con JWT, hallazgos, suscripciones y bandeja ([PR #8](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/8)).
- [x] **Integración:** 36 pruebas Python, navegador simulado y flujo real de dos cuentas, hallazgo, extravío, páginas públicas y alertas en `02-separacion`.
- [x] **Medición local:** 20/20 suscriptores recibieron la alerta en 5.55 s desde la respuesta de publicación; falta repetirlo mediante un script de evidencia.
- [ ] **Mascotas:** Luisa añade edición de ficha propia; Amy añade registro independiente y selección de una ficha guardada al publicar, como pide el PRD.
- [ ] **Equipo:** PDF final, pitch y defensa individual.
- [ ] **Equipo:** cerrar compromisos adicionales del PRD: identidad separada, Traefik, dos copias de reportes y pruebas de fallas reproducibles, o documentar un ajuste honesto del alcance.

La aplicación web distribuida funciona en `02-separacion`. Para ejecutarla, cambiar a esa rama y seguir su README. `main` aún no sustituye a esa rama como entrega final.
