# The Four Nodes · búsqueda comunitaria de mascotas

Proyecto final de Sistemas Distribuidos 2027-1 de la FI-UNAM. Una persona publica el extravío de su mascota y comparte el enlace del reporte; otras personas pueden registrar hallazgos y seguir un municipio para recibir alertas. El alcance y las decisiones están en [docs/PRD.md](docs/PRD.md).

## Equipo

1. **Oscar Ivan Montiel Juarez** — [@Montiel-Oscar](https://github.com/Montiel-Oscar)
2. **Luisa María Segura Cedeño** — [@LuisaCedeno](https://github.com/LuisaCedeno)
3. **Cecilia Ximena Solis Cisneros** — [@CeciliaXimenaSolisCisneros](https://github.com/CeciliaXimenaSolisCisneros)
4. **Amy Valentina Veraza García** — [@Amyv19](https://github.com/Amyv19)

## Primera entrega: `01-monolito`

La rama `01-monolito` guarda la primera entrega: una aplicación FastAPI y una base PostgreSQL levantadas con Docker Compose. Su flujo principal permite **publicar un extravío**, capturando o seleccionando la mascota y obteniendo un enlace público. El monolito usa una cuenta de demostración. La entrega final distribuida está en `main` y `02-separacion`.

**Entrega del curso:** sábado 17 de octubre de 2026, antes de las 07:00. El equipo comparte la liga del repositorio en su comentario de la Discussion #44 cuando la rama `01-monolito` tenga el flujo principal funcionando.

Las instrucciones de colaboración y el reparto originales permanecen en la rama histórica `01-monolito`.

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

Las tres ramas permanentes son `main` (entrega final), `01-monolito` (primera entrega terminada) y `02-separacion` (desarrollo distribuido terminado). `main` y `02-separacion` contienen el mismo commit de la versión final.

## Versión final distribuida: `main` y `02-separacion`

La aplicación final permite marcar en un mapa la ubicación aproximada de extravíos y hallazgos, además de escribir municipio, colonia y referencia. Quien encuentre una mascota puede enviar un mensaje privado desde el enlace del reporte; quien lo publicó puede leerlo y responder en **Comunidad → Mensajes**, sin publicar su teléfono. Tiene tres servicios FastAPI: identidad, reportes (dos réplicas) y alertas. Traefik publica únicamente `http://localhost:8000`; PostgreSQL guarda tres bases lógicas en una instancia. El [diagrama de arquitectura](docs/ARQUITECTURA_FINAL.md), el [PRD](docs/PRD.md), los [resultados medidos](docs/RESULTADOS_FINALES.md) y la [rúbrica](RUBRICA.md) documentan la entrega.

El [mapa y su migración](docs/MAPA.md) guardan coordenadas para reportes nuevos y muestran un punto rojo con un círculo de 3 km en el enlace público. Las alertas siguen filtradas por municipio.

### Arranque sin pasos ocultos

Requisitos: Docker con Compose y Python 3. Desde la raíz del repositorio:

```bash
python3 scripts/setup_env.py
docker compose up --build -d
python3 scripts/smoke_02.py
python3 scripts/verify_gateway.py
```

Abrir [la aplicación](http://localhost:8000/), [la comunidad](http://localhost:8000/comunidad) o [la API de reportes](http://localhost:8000/docs). `setup_env.py` crea las claves locales en `.env` si faltan; conserva las existentes para mantener cuentas y volumen. `.env` está ignorado por Git. Si se usó una versión anterior, `docker compose down --remove-orphans` antes de iniciar conserva el volumen. Para detener: `docker compose down`. Sólo Traefik publica un puerto al host.

**Probar el contacto sin teléfono:** crea dos cuentas. Con A publica un extravío y deja desmarcada la opción de mostrar teléfono. Con B abre el enlace público, entra en la misma pestaña y usa **Enviar mensaje privado**. Vuelve a A, abre `/comunidad#messages`, pulsa **Actualizar mensajes**, abre la conversación y responde. En B, entra a **Mensajes** para leer la respuesta. Los mensajes se guardan en la base de reportes y solo los ven esas dos cuentas. La bandeja se consulta al abrirla y cada 30 segundos mientras la página está visible; no hay correo, SMS ni notificaciones push.

### Pruebas

```bash
docker compose run --rm --volume "$PWD:/workspace" reportes_a sh -c "pip install -q '.[dev]' && pytest -q"
python3 scripts/smoke_contact.py
python3 scripts/resilience_20_subscribers.py --subscribers 20 --trials 3 --timeout 150 --with-faults
```

La suite Python pasó **40 pruebas**. El recorrido HTTP, el balanceo con una réplica detenida y la demo real de dos cuentas en Chrome pasaron. En tres ensayos locales de 20 suscriptores, los 20 recibieron una sola alerta por reporte; el máximo observado hasta consultar todas las bandejas fue **10.307 s**. La prueba de caída de `alertas` mantuvo la publicación y entregó la alerta tras reiniciar. Con PostgreSQL detenido, una nueva publicación no se confirmó y el reporte fallido no apareció tras la recuperación. Estos resultados son locales y no garantizan disponibilidad ante caída de la instancia de PostgreSQL.

### Entrega y presentación

- [Reporte final PDF](docs/reporte-final.pdf), elaborado desde [fuentes LaTeX](docs/reporte_proyecto/main.tex) basadas en el estilo del reporte de referencia.
- [Presentación en Canva](https://canva.link/ceqim33wqulq7q9) y [copia PDF de 10 diapositivas](docs/pitch/diapositivas.pdf).
- [Resultados y fallas](docs/RESULTADOS_FINALES.md).

**Equipo:** Oscar Iván Montiel Juárez, Luisa María Segura Cedeño, Cecilia Ximena Solís Cisneros y Amy Valentina Veraza García. La entrega del curso es el **28 de noviembre de 2026 antes de las 07:00**, hora de Ciudad de México.

### Límites

El mapa permite marcar un punto aproximado y muestra un radio de 3 km en reportes nuevos. Los reportes anteriores conservan su ubicación escrita sin punto. La cartografía necesita Internet para cargar las teselas de OpenStreetMap; el código de Leaflet se sirve localmente. No hay despliegue público, HTTPS, notificaciones al teléfono ni alta disponibilidad de PostgreSQL. Los tres servicios usan tres bases lógicas dentro de una sola instancia física. La bandeja web se actualiza por consulta periódica y las alertas son eventualmente consistentes.
