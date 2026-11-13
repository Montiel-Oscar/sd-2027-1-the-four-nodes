# Plan de cierre del proyecto final · 13 de noviembre de 2026

**Entrega:** sábado 28 de noviembre de 2026, **antes de las 07:00**, hora de Ciudad de México. El código y `docs/reporte-final.pdf` deben estar en el repositorio antes de ese momento. Cada integrante debe explicar su contribución en el pitch y defender las decisiones técnicas.

## Estado y prioridad

La rama `02-separacion` ya permite registrar mascotas, publicar extravíos y hallazgos, seguir un municipio y leer alertas desde la web. Se probó con Docker, PostgreSQL y navegador real; la suite tiene 36 pruebas aprobadas. La [rúbrica](../RUBRICA.md) acepta incluso un monolito modular si funciona y está bien explicado. Por ello, **el PDF, el pitch y la demo reproducible tienen prioridad sobre agregar procesos por su cuenta**.

El [PRD](PRD.md), sin embargo, promete una etapa final con identidad separada, Traefik y dos copias de reportes. Para cumplir lo que el equipo escribió, este plan asigna esas piezas. Si alguna pone en riesgo la demo estable, el equipo debe conservar `02-separacion` funcionando, actualizar el PRD con el alcance realmente entregado y explicar la decisión en el reporte; no declarar implementado algo que no se pueda demostrar.

## Reparto de cuatro tareas paralelas

Cada persona crea una rama temporal desde `02-separacion` y abre PR **hacia `02-separacion`**. No modificar archivos de otra tarea sin acordar el contrato. Los cuatro trabajos empiezan en paralelo; la integración y el PDF final tienen pasos posteriores.

| Responsable | Rama temporal sugerida | Archivos principales | Resultado que debe entregar |
|---|---|---|---|
| **Oscar Iván Montiel Juárez** | `trabajo/oscar-gateway-final` | `compose.yaml`, `traefik/`, `Dockerfile`, `docs/ARQUITECTURA_FINAL.md` | Traefik como entrada única y dos copias de reportes sin estado, con ruta pública y prueba de que una copia puede detenerse sin perder todas las solicitudes. **Esta tarea se deja asignada; no está implementada en este plan.** |
| **Ceci Ximena Solís Cisneros** | `trabajo/ceci-identidad-final` | `app/identity/`, `app/core/auth.py`, nuevo punto de entrada de identidad, migración/inicialización de su base y pruebas | Identidad en proceso y base lógica propios; registro/login en el mismo contrato HTTP, JWT verificable localmente por reportes y alertas, y datos previos conservados o migrados sin borrar volúmenes. |
| **Luisa María Segura Cedeño** | `trabajo/luisa-evidencia-final` | `scripts/`, `tests/`, `docs/RESULTADOS_FINALES.md`, `docs/reporte-final.pdf` | Ensayos reproducibles de 20 suscriptores, reintento/ACK, caída y reinicio de alertas, caída de PostgreSQL y persistencia; tabla de tiempos. Coordina y ensambla el PDF final con las secciones aportadas por todos. |
| **Amy Valentina Veraza García** | `trabajo/amy-demo-final` | `app/web/`, `app/web/tests/`, `docs/pitch/` | Adaptar la web a una sola entrada por Traefik cuando esté disponible, conservar los flujos y el polling, revisar móvil/accesibilidad, dejar un guion de demo y preparar el pitch con intervenciones de los cuatro. |

### Contratos para trabajar en paralelo

1. **Ceci ↔ Oscar:** mantener `POST /api/usuarios/register`, `POST /api/usuarios/login` y `GET /api/usuarios/me` iguales. Identidad expondrá internamente el puerto acordado en Compose; Oscar enrutará `/api/usuarios/` hacia ella. Reportes no debe consultar identidad al publicar, solo verificar JWT.
2. **Oscar ↔ Amy:** la entrada final será una sola URL local, por ejemplo `http://localhost:8000`. Las llamadas web a alertas serán rutas relativas `/api/alertas/...` cuando Traefik esté activo. Amy puede preparar ese cambio sin tocar Compose.
3. **Luisa ↔ todos:** los scripts de prueba usarán rutas y variables configurables para ejecutarse primero contra `02-separacion` y luego contra la arquitectura final. Las mediciones deberán registrar inicio, respuesta de publicación, creación de alerta y visualización en web; un único ensayo local de 5.55 s no es suficiente como evidencia final.
4. **PDF:** cada integrante entrega a Luisa texto e imágenes originales de su parte. Luisa reúne portada, problema, dos diagramas, al menos tres decisiones con alternativas, fallas, instrucciones de ejecución, límites y contribuciones. El archivo final va exactamente en `docs/reporte-final.pdf`.

## Criterios de aceptación por tarea

### Oscar · gateway y réplicas

- `docker compose up --build` levanta todos los componentes con la configuración documentada, sin editar archivos ni ejecutar comandos ocultos.
- La página inicial, `/api/usuarios/`, `/api/mascotas/`, `/api/reportes/` y `/api/alertas/` responden desde un solo origen. La API interna del outbox no se expone al navegador por accidente.
- Dos procesos de reportes comparten su base y la clave de firma. Después de detener uno, el otro sigue respondiendo; los reintentos de publicación conservan la `Idempotency-Key`.
- El README y un diagrama muestran la entrada, el descubrimiento por DNS, el balanceo, la base de cada servicio y el comportamiento ante caída. Aporta esa sección al PDF y prepara una explicación de aproximadamente un minuto.

### Ceci · identidad separada

- El proceso de identidad posee las cuentas y contraseñas; reportes y alertas no crean ni modifican su tabla. Tres bases lógicas están documentadas y la inicialización es idempotente con un volumen existente.
- Registro, login, `/me`, token válido, token alterado/vencido, correo duplicado y privacidad entre usuarios pasan las pruebas. Los enlaces públicos siguen abiertos sin token.
- Detener identidad no impide publicar con un JWT vigente; crear una cuenta o iniciar sesión sí falla de forma clara mientras está detenido.
- Aporta al PDF el diagrama de propiedad de datos y la decisión de verificar el token localmente. Prepara una explicación de aproximadamente un minuto.

### Luisa · resiliencia y PDF

- Un script repetible crea hasta 20 suscriptores, publica ambos tipos de reporte y comprueba alerta única para cada destinatario. Reporta tiempos en varias ejecuciones; la creación de alerta debe tardar menos de 2 min 30 s y la web abierta mostrarla en menos de 3 min.
- Detener `alertas` no impide publicar; al reiniciarlo se procesa el evento una vez desde la perspectiva del usuario. Probar también reentrega tras ACK perdido o repetido, suscripción posterior al evento y reinicio de contenedores.
- Detener PostgreSQL debe impedir confirmar una publicación no guardada. Documentar el fallo esperado y el regreso del servicio sin borrar datos.
- El PDF final se puede abrir, incluye todos los nueve puntos de la rúbrica, atribuye trabajo real a cada persona y contiene resultados medidos. Prepara una explicación de aproximadamente un minuto sobre consistencia eventual y fallas.

### Amy · web, demo y pitch

- Registro, login, extravío, hallazgo, filtros, suscripción, bandeja y páginas públicas funcionan desde la entrada final. Las solicitudes privadas llevan Bearer y las públicas no lo exigen.
- Probar con Chrome/Edge y en un teléfono o emulación a 390 px y escritorio. Verificar teclado, foco visible, errores 401/409/red, teléfono con y sin consentimiento, enlace copiable, bandeja vacía y cierre de sesión.
- El guion del pitch muestra problema, solución y demo real en el tiempo asignado por el profesor. Cada integrante presenta una parte; preparar una ruta de demostración de respaldo y capturas si falla la red local.
- Aporta al PDF el flujo funcional con capturas y la sección de límites de la interfaz. Prepara una explicación de aproximadamente un minuto sobre experiencia del usuario.

## Orden de integración y fechas de control

1. **Hasta el 18 de noviembre:** cuatro ramas temporales creadas desde el mismo `02-separacion`; acordar puertos/rutas. Cada PR muestra qué cambió, cómo se ejecutó y resultados. La documentación y el pitch pueden avanzar desde el primer día.
2. **Hasta el 21 de noviembre:** integrar Ceci y Oscar en ese orden, resolviendo Compose una sola vez. Tras cada merge, correr la suite, `scripts/smoke_02.py` y el flujo web real. Si falla un flujo básico, reparar antes del siguiente merge.
3. **Hasta el 24 de noviembre:** integrar Amy y Luisa con las pruebas finales. Cada cambio se incorpora a `02-separacion`; las ramas temporales se borran después de fusionar. La demo debe tener un comando de arranque y un guion estable.
4. **Hasta el 26 de noviembre:** Luisa ensambla `docs/reporte-final.pdf`; el equipo revisa que los diagramas describan el código realmente entregado. Ensayar el pitch con cámara y preguntas cruzadas.
5. **27 de noviembre:** prueba en limpio siguiendo solo el README, revisión final del PDF y slides, comprobación de contribuciones de los cuatro y merge de `02-separacion` a `main` si todo pasa. Subir antes de las 07:00 del **28 de noviembre**.

## Checklist de la rúbrica

- [x] Prototipo distribuido básico funcionando en `02-separacion`: cuatro flujos, dos procesos y dos bases lógicas.
- [x] Arranque y prueba local iniciales; 36 pruebas Python, navegador simulado y navegador real con dos cuentas.
- [ ] Arquitectura final del PRD, o PRD actualizado con una decisión explícita y defendible.
- [ ] Pruebas de falla y tiempos automatizadas y repetibles con evidencia.
- [ ] README de arranque en limpio sin pasos escondidos.
- [ ] `docs/reporte-final.pdf` con todos los apartados obligatorios.
- [ ] Pitch ensayado, demo preparada y cada integrante listo para responder preguntas técnicas.
