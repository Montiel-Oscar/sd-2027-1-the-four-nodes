# Estado de la entrega final · 26 de noviembre de 2026

`02-separacion` integra tres servicios, dos réplicas de reportes, tres bases lógicas, web y resultados de resiliencia. Oscar fusionó el PR #20 de Luisa y reparó la mezcla accidental de archivos antiguos de autenticación y alertas incluida por una rama previa. Conservó su edición de mascotas y su script, corrigiendo el contrato del extravío y ejecutándolo contra los servicios reales.

## Evidencia

- 39 pruebas Python aprobadas; registro, JWT, mascotas propias, edición, reportes, outbox, alertas y privacidad.
- `scripts/smoke_02.py` pasó por Traefik con identidad separada; `scripts/verify_gateway.py` pasó con una réplica detenida.
- Chrome completó un recorrido real con dos cuentas, fichas separadas/reutilizadas, ambos reportes y bandeja.
- Tres ensayos de 20 suscriptores: 20/20 alertas únicas por reporte; máximo local 10.307 s hasta consultar todas las bandejas.
- Alertas detenidas: publicación 201 y entrega tras reinicio. PostgreSQL detenido: intento HTTP 500 sin publicación confirmada. Identidad detenida: login indisponible y publicación 201 con JWT vigente.
- `docs/reporte-final.pdf` incluye los nueve apartados de `RUBRICA.md`; `docs/pitch/` incluye slides y guion de cada voz y clic.

El mapa guarda coordenadas en reportes nuevos y muestra un punto rojo con radio de 3 km; los anteriores conservan sólo texto. La instancia PostgreSQL sigue siendo un punto de falla. Estas pruebas son locales y no certifican disponibilidad pública ni entrega push. Los cuatro integrantes deben ensayar el pitch y su defensa técnica antes de presentarse.
