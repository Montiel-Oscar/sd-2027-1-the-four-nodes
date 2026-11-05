# Servicio de alertas · `02-separacion`

`app.alerts.main:app` se ejecuta en un proceso FastAPI propio, puerto 8001. Usa la base lógica `four_nodes_alerts` y solo consulta reportes mediante el feed HTTP interno. No importa ni escribe las tablas de reportes.

`compose.yaml` le pasa `DATABASE_URL_ALERTS`, `AUTH_SECRET`, `INTERNAL_API_TOKEN` e `INTERNAL_API_URL`. El inicializador crea su base si no existe, incluso cuando el volumen viene de `01-monolito`. El trabajador consulta cada 10 segundos, guarda las alertas y luego confirma el evento; un reintento no duplica la bandeja por la restricción `(event_id, recipient_id)`.

El contrato de suscripciones y bandeja está en [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md#alertas-luisa--amy). El estado de integración, las pruebas y lo que falta están en [ESTADO_02_SEPARACION.md](../../docs/ESTADO_02_SEPARACION.md).
