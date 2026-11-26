# Cierre de la rúbrica · 26 de noviembre de 2026

**Fecha límite:** sábado 28 de noviembre de 2026 antes de las 07:00 (Ciudad de México). La entrega se consulta en `main`; `01-monolito` conserva la primera etapa y `02-separacion` la versión distribuida.

| Rubro | Evidencia en el repositorio | Estado |
|---|---|---|
| Prototipo (30 %) | README, `compose.yaml`, `app/`, `traefik/`, 38 pruebas Python, `scripts/smoke_02.py`, `scripts/verify_gateway.py`, `scripts/resilience_20_subscribers.py` y recorrido real de Chrome | Terminado y probado localmente |
| Reporte PDF (30 %) | [Reporte final](reporte-final.pdf) y [fuentes LaTeX](reporte_proyecto/main.tex): portada, problema, dos diagramas, decisiones y alternativas, fallas, arranque, límites y aportes | Terminado |
| Pitch (20 %) | [Siete diapositivas](pitch/diapositivas.pdf), [HTML](pitch/diapositivas.html) y [guion de cuatro voces y clics](pitch/GUION_FINAL.md) | Preparado; ensayo oral del equipo pendiente |
| Defensa individual (20 %) | [Reparto técnico](pitch/GUION_FINAL.md), historial de PR y commits, preguntas de defensa | Cada integrante debe ensayar y responder por su contribución |

## Verificación técnica

- [x] Registro, login y `/me` en identidad separada; tercera base lógica; migración idempotente de usuarios anteriores.
- [x] Mascotas propias, edición con control de dueño y descripción congelada en reportes publicados.
- [x] Extravío y hallazgo, enlace público, suscripción por municipio y bandeja de alertas.
- [x] Traefik como única entrada pública y dos réplicas de reportes.
- [x] Outbox, ACK y deduplicación; 20/20 suscriptores en tres ensayos de ambos tipos de reporte. Máximo local observado: 10.307 s.
- [x] Caída de alertas, caída de una réplica, caída de identidad y caída de PostgreSQL comprobadas; sus límites están documentados.
- [x] README, reporte, diapositivas, guion y procedimiento de demo completos.
- [ ] Ensayo presencial o por videollamada con cámara de los cuatro integrantes; no puede verificarse por código.

## Atribución y estado de PR

Oscar integró la arquitectura de entrada, dos réplicas, la separación final de identidad, migración, validación y reporte. Ceci contribuyó al trabajo de identidad en etapas anteriores; la separación final fue cerrada por Oscar al no existir un PR final de Ceci. Luisa entregó edición de mascotas y el script de resiliencia en los PR #18 y #20; Oscar corrigió el script y ejecutó las mediciones. Amy entregó la interfaz, las diapositivas y el guion base en el PR #15; Oscar actualizó la presentación y escribió el guion final de defensa. El historial de Git conserva la autoría de cada cambio original.

## Límites declarados

El único PostgreSQL físico sigue siendo un punto de falla. No hay mapa, despliegue público, HTTPS ni notificaciones push. El tiempo de 10.307 s corresponde a lectura por API en entorno local; la página consulta la bandeja periódicamente y no se midió el instante en que una persona la ve.
