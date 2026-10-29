# Alertas · etapa posterior

Esta carpeta delimita el módulo de alertas dentro del monolito. Para **la primera entrega `01-monolito`**, el requisito es guardar un evento pendiente al publicar un extravío; Oscar lo hace en `app/reports/`. La bandeja y el servicio separado de alertas corresponden a `02-separacion` según [el PRD](../../docs/PRD.md).


## Trabajo de Luisa en `02-separacion`

Se creó `trabajo/luisa-alertas-v1` desde `02-separacion`. Esta carpeta será un proceso FastAPI independiente con su propia base lógica, suscripciones, bandeja y trabajador que consulta el feed de Oscar por HTTP. Sigue los pasos detallados de [PLAN_02_SEPARACION.md](../../docs/PLAN_02_SEPARACION.md#luisa--proceso-de-alertas-trabajoluisa-alertas-v1) y las rutas de [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md#alertas-luisa--amy). El worker confirma el evento solo después de confirmar alertas en su base; la restricción única por evento y destinatario evita duplicados en reintentos. Publica un PR con base `02-separacion` y demuestra que una caída de alertas no impide publicar.
