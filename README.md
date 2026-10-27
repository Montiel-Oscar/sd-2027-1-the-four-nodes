# The Four Nodes · búsqueda comunitaria de mascotas

Proyecto final de Sistemas Distribuidos 2027-1 de la FI-UNAM. Una persona publica el extravío de su mascota y comparte el enlace del reporte; otras personas pueden registrar hallazgos y seguir un municipio para recibir alertas. El alcance y las decisiones están en [docs/PRD.md](docs/PRD.md).

## Equipo

1. **Oscar Ivan Montiel Juarez** — [@Montiel-Oscar](https://github.com/Montiel-Oscar)
2. **Luisa María Segura Cedeño** — [@LuisaCedeno](https://github.com/LuisaCedeno)
3. **Cecilia Ximena Solis Cisneros** — [@CeciliaXimenaSolisCisneros](https://github.com/CeciliaXimenaSolisCisneros)
4. **Amy Valentina Veraza García** — [@Amyv19](https://github.com/Amyv19)

## Primera entrega: `01-monolito`

La rama `main` contiene la documentación. La rama `01-monolito` contiene una sola aplicación FastAPI y una base PostgreSQL levantadas con Docker Compose. El primer flujo a completar es **publicar un extravío**, capturando o seleccionando la mascota y obteniendo un enlace público. El monolito puede usar una cuenta de demostración; la separación en servicios vendrá después.

**Entrega del curso:** sábado 17 de octubre de 2026, antes de las 07:00. El equipo comparte la liga del repositorio en su comentario de la Discussion #44 cuando la rama `01-monolito` tenga el flujo principal funcionando.

La [guía de colaboración](docs/COMO_COLABORAR.md) explica cómo entrar a la rama, crear una rama personal y entregar cambios con GitHub Desktop o Git. El [reparto de tareas](docs/REPARTO_01_MONOLITO.md) indica qué hará cada integrante y cómo integrar el trabajo.

## Estado del monolito · 22 de octubre de 2026

La rama `01-monolito` integra mascotas, reportes, una cuenta de demostración y una interfaz web. Se puede publicar un extravío con una mascota nueva, reintentar sin duplicarlo y abrir su página pública. El reporte y el evento pendiente se guardan en una sola transacción. También se pueden registrar y consultar fichas propias de mascotas.

Luisa entregó el módulo de mascotas en la [solicitud #2](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/2), Amy la interfaz en la [#3](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/3) y Oscar el módulo de reportes en la [#1](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/1). No se encontró rama ni solicitud de Cecilia; el mínimo de identidad de demostración se completó durante la integración. El registro real de usuarios y el envío de alertas corresponden a etapas posteriores del PRD.

## Levantar la aplicación

En la rama `01-monolito`, con Docker y Docker Compose instalados:

```bash
cp .env.example .env
docker compose up --build
```

Abrir `http://localhost:8000/` para la página inicial, `http://localhost:8000/docs` para la API y `http://localhost:8000/health/ready` para comprobar la conexión con PostgreSQL. El archivo `.env` es local y no se sube a GitHub. Para detener la aplicación, usar `Ctrl+C` y después `docker compose down`; el volumen de la base conserva los datos.

## Ramas del proyecto

`main` → versión estable. `01-monolito` → primera entrega ejecutable. `02-separacion` → versión 1 distribuida en desarrollo. Después vienen `03-identidad-gateway` y `04-resiliencia`, según el PRD. Las ramas personales de cada etapa parten de su rama de etapa y vuelven a ella mediante revisión del equipo.

## Primera versión distribuida: `02-separacion`

Esta rama inicia la separación entre reportes y alertas. El [plan de cuatro tareas](docs/PLAN_02_SEPARACION.md), los [contratos de API y eventos](docs/CONTRATOS_02_SEPARACION.md) y la [guía de trabajo](docs/COMO_TRABAJAR_02.md) definen qué debe implementar cada integrante y cómo integrar sus Pull Requests. **Es una rama en desarrollo**: `01-monolito` sigue siendo la versión funcional hasta que pasen las pruebas de aceptación de la nueva etapa.
