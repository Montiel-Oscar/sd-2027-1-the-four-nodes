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

## Levantar el monolito histórico

En la rama `01-monolito`, con Docker y Docker Compose instalados:

```bash
cp .env.example .env
docker compose up --build
```

Abrir `http://localhost:8000/` para la página inicial, `http://localhost:8000/docs` para la API y `http://localhost:8000/health/ready` para comprobar la conexión con PostgreSQL. El archivo `.env` es local y no se sube a GitHub. Para detener la aplicación, usar `Ctrl+C` y después `docker compose down`; el volumen de la base conserva los datos.

## Ramas del proyecto

Las tres ramas permanentes son `main` (referencia del proyecto), `01-monolito` (primera entrega terminada) y `02-separacion` (segunda entrega en integración). Las ramas personales son temporales: parten de su rama de etapa y se borran después de integrar el PR. Las etapas posteriores del PRD todavía no tienen rama.

## Versión distribuida: `02-separacion`

La rama `02-separacion` tiene Traefik, dos réplicas de reportes, un proceso de alertas y dos bases lógicas en PostgreSQL. El [diagrama y comportamiento ante fallas](docs/ARQUITECTURA_FINAL.md), los [contratos](docs/CONTRATOS_02_SEPARACION.md) y el [estado detallado](docs/ESTADO_02_SEPARACION.md) explican la implementación y lo pendiente.

La [rúbrica del proyecto final](RUBRICA.md) y el [plan de cierre por integrante](docs/PLAN_CIERRE_RUBRICA.md) guían la entrega del **28 de noviembre de 2026 antes de las 07:00** (hora de Ciudad de México).

### Lista de avance

- [x] **Oscar:** hallazgos, listas públicas, publicación idempotente y feed/ACK del outbox ([PR #4](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/4)).
- [x] **Ceci:** registro, login, JWT y autorización compartida ([PR #7](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/7)).
- [x] **Luisa + integración:** API y trabajador de alertas, bandeja privada, segunda base lógica y Compose ([PR #5](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/5)); el PR entró por error a `main` y su commit se incorporó también a `02-separacion`.
- [x] **Amy:** interfaz de registro/login, hallazgos, suscripciones, bandeja, Bearer JWT y páginas públicas ([PR #8](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/8)).
- [x] **Integración:** 36 pruebas Python, prueba de navegador con APIs simuladas, flujo web real con dos cuentas y entrega de ambas alertas; publicación durante la caída de `alertas` y entrega única tras reiniciarlo.
- [x] **Medición local:** 20/20 suscriptores recibieron la alerta en 5.55 s desde la respuesta de publicación; un ensayo local, pendiente convertirlo en prueba reproducible.
- [x] **Oscar:** Traefik, dos réplicas de reportes, feed interno aislado y prueba de publicación y alerta con una réplica detenida. La tercera base de identidad sigue pendiente de Ceci.
- [ ] **Ceci:** separar identidad en proceso y base propios, migrar los datos existentes y enrutar `/api/usuarios` hacia ese proceso.
- [ ] **Mascotas:** Luisa añade edición de ficha propia; Amy añade registro independiente y selección de una ficha guardada al publicar, como pide el PRD.
- [ ] **Amy:** adaptar la web al origen único y entregar guion, demo y pitch para los cuatro.
- [ ] **Luisa:** pruebas repetibles de fallas y tiempos; reunir las aportaciones del equipo en `docs/reporte-final.pdf`.
- [ ] **Oscar:** integrar los PR finales, probar el arranque en limpio y fusionar `02-separacion` a `main` antes de la entrega.

### Arranque y pruebas de `02-separacion`

Con Docker, Docker Compose y Python 3 instalados, desde la raíz del repositorio:

```bash
git switch 02-separacion
python3 scripts/setup_env.py
docker compose up --build -d
python3 scripts/smoke_02.py
python3 scripts/verify_gateway.py
```

Abrir `http://localhost:8000/`, `http://localhost:8000/docs` y `http://localhost:8000/health/ready`. `setup_env.py` crea `.env` con claves locales si falta y conserva las existentes, para no invalidar un volumen previo. `.env` no se sube a Git. La web actual todavía puede llamar al puerto `8001`, servido también por Traefik como compatibilidad hasta que Amy integre el origen único. `verify_gateway.py` detiene y reinicia una réplica y crea datos de prueba. Si se viene de una versión anterior de Compose, ejecutar una vez `docker compose down --remove-orphans` antes de `up`; este comando conserva el volumen. Para detener: `docker compose down`.

La suite Python se ejecuta sin instalar dependencias en el host:

```bash
docker compose run --rm --volume "$PWD:/workspace" reportes_a sh -c "pip install -q '.[dev]' && pytest -q"
```

Las instrucciones individuales y todos los pendientes de la última entrega están en [docs/PLAN_CIERRE_RUBRICA.md](docs/PLAN_CIERRE_RUBRICA.md). Cada compañera crea su rama temporal desde `02-separacion` y abre un PR hacia `02-separacion`.
