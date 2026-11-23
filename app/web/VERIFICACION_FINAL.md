# Amy · cierre de rúbrica

Rama `trabajo/amy-demo-final` desde `origin/02-separacion`, según `docs/PLAN_CIERRE_RUBRICA.md`. El PR se dirige a `02-separacion`. No se cambian las APIs, Compose ni Traefik, que pertenecen a las otras tareas.

## Cambios

La sección «Mis mascotas» en `/comunidad#pets` registra una ficha con `POST /api/mascotas`, sin publicar reporte. Lista solo las propias con `GET /api/mascotas` y enlaza al formulario con la ficha seleccionada. El primer paso de extravío permite elegir una guardada y publica `pet_id`, o conservar la captura nueva y publicar `pet`; nunca envía ambos. La vista previa muestra la ficha escogida. Al cerrar sesión se vacían fichas y selector, y se descartan respuestas privadas pendientes.

Alertas usa rutas relativas `/api/alertas/...`, a través de la entrada final de Traefik. La web no llama al puerto temporal 8001. Oscar puede retirar esa entrada heredada cuando integre este PR. Se conserva consulta cada 30 s visible, Bearer privado, enlaces públicos y reintentos idempotentes de ambos reportes.

Se refuerzan el foco visible y el contraste de navegación, controles y mensajes de fichas. Se comprueba emulación a 390 px y escritorio. El registro independiente no tiene contrato de idempotencia; ante respuesta perdida se indica actualizar fichas antes de repetir, sin afirmar que no pueda duplicarse.

## Evidencia reproducible

Con las dependencias del proyecto, Playwright y Edge instalados en el entorno de pruebas:

```powershell
python -m pytest -q
python app/web/tests/verify_browser.py
python app/web/tests/verify_final_demo.py
python docs/pitch/export_slides.py
```

Se puede usar Chrome definiendo `PLAYWRIGHT_BROWSER` con su ejecutable. La sintaxis de los cuatro scripts se verifica con `Get-Content -Raw RUTA | node --check`.

| Criterio de Amy | Comprobación local |
|---|---|
| Ficha independiente, lista propia y reutilización | Recorrido con APIs reales por TestClient y SQLite temporal; cuenta A registra y reutiliza Luna, cuenta B crea Sol junto con un reporte. B no lista Luna y recibe 404 al consultar su ID. |
| Ambos modos de publicación | Navegador verifica `pet_id` sin `pet` para ficha elegida; conserva creación conjunta y reintento con la misma clave. |
| Entrada única | La prueba de navegador rechaza solicitudes a otro origen. Todas las llamadas web a alertas son relativas. La configuración real de Traefik la valida Oscar. |
| Flujos públicos y privados | Dos cuentas, hallazgo, extravíos, filtro, suscripción, baja, bandeja, enlaces públicos sin sesión y limpieza al salir. |
| Teléfono y copia | Un extravío sin teléfono público y un hallazgo con número ficticio autorizado; botón de copiar o mensaje alternativo con URL. |
| Móvil y teclado | Sin desbordamiento a 390/768/1440 en prueba simulada; recorrido local también a 390 y escritorio, navegación mediante Tab y foco visible. |
| Errores y reintento | APIs simuladas fuerzan fallo de red, 401 y 409; se verifica conservación de clave, cambio de clave al editar, bandeja vacía y eliminación de datos privados. |
| Pitch y aporte al PDF | Siete diapositivas HTML/PDF, guion con cuatro intervenciones y respaldo, diagrama funcional, capturas originales y texto para Oscar en `docs/pitch/`. |

`verify_final_demo.py --base-url http://localhost:8000 --output docs/pitch/capturas-en-vivo` ejecuta el recorrido con servicios reales y genera otro juego de capturas. Crea datos ficticios con sufijos únicos y no borra registros ni volúmenes. Sin `--base-url`, usa rutas y lógica reales en SQLite y transporte local, procesa y reentrega eventos explícitamente y no ejecuta el trabajador temporizado ni el balanceo.

## Resultados y límites · 15 de noviembre de 2026

- 36 pruebas Python aprobadas.
- Prueba con APIs simuladas aprobada en Microsoft Edge y Google Chrome.
- Recorrido de dos cuentas contra APIs reales locales aprobado en Edge; capturas y `entorno.json` en `docs/pitch/capturas/`.
- PDF de siete páginas abierto y comprobado con texto legible; navegación y ausencia de desbordamiento de slides verificadas.

Se inició Docker Desktop y se prepararon las claves locales con `python scripts/setup_env.py`, conservando las existentes. El intento `docker compose up --build -d` descargó Traefik pero se detuvo al resolver `python:3.12-slim`: timeout al obtener el token de Docker Hub (`auth.docker.io/token`). Por eso no se presenta la prueba local como evidencia de PostgreSQL, balanceo, recuperación de contenedores o latencia con 20 suscriptores. No se borraron volúmenes. El cierre distribuido, la medición y el ensayo conjunto quedan pendientes de un arranque exitoso. Tampoco se afirma terminada la separación final de identidad o la edición de fichas de las tareas de Ceci y Luisa. El PDF final del reporte sigue asignado a Oscar.
