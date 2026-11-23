# Interfaz distribuida de Amy

Rama `trabajo/amy-web-v1`, creada desde `origin/02-separacion`. Cambios limitados a `app/web/`; se conservan los contratos de API.

## Implementación

- `/`: extravío guiado con Bearer y acceso a cuenta sin abandonar el formulario.
- `/comunidad`: registro, inicio, listas públicas filtrables de ambos tipos, publicación de hallazgo, suscripciones y bandeja privada.
- `/reportes/hallazgos/{id}`: página pública, con la misma protección de UUID que extravíos.
- JWT en `sessionStorage`; cierre de sesión y 401 privados eliminan el token. La contraseña no se guarda en almacenamiento del navegador.
- Ambos formularios conservan cuerpo e `Idempotency-Key` tras fallo de red mientras la página siga abierta. Cambiar el cuerpo genera otra clave. Renovar el token no cambia el intento. Recargar descarta el intento pendiente.
- Fechas ISO con zona horaria, longitudes del contrato y teléfono únicamente con consentimiento explícito. Estados de validación, 401, 409 y conexión.
- Alertas usa `http://localhost:8001`; abrir la web en `http://localhost:8000` para cumplir el CORS de la etapa. La configuración es para demo local.
- Bandeja consultada cada 30 segundos mientras la página esté visible y al volver a ella. Al salir se limpian datos privados y se ignoran respuestas pendientes de la sesión anterior.
- Textos de API mediante `textContent`; enlaces de alertas limitados a rutas públicas de reportes del mismo origen.

## Verificado el 12 de noviembre de 2026

```powershell
.venv/Scripts/python -m pytest -q
python app/web/tests/verify_browser.py
Get-Content -Raw app/web/static/app.js | node --check
Get-Content -Raw app/web/static/session.js | node --check
Get-Content -Raw app/web/static/community.js | node --check
```

36 pruebas Python aprobadas y sintaxis válida en los tres scripts. La prueba de navegador requiere Playwright y Microsoft Edge; en Linux se puede usar Chrome con `PLAYWRIGHT_BROWSER=/usr/bin/google-chrome python app/web/tests/verify_browser.py`.

Edge usa APIs simuladas: verifica registro, Bearer, hallazgo y extravío con respuesta perdida y reintento con la misma clave, nueva clave al cambiar cuerpo, consentimiento, suscripción, consulta periódica, cierre de sesión y reporte público con texto que parece HTML. Comprueba ausencia de desbordamiento a 390, 768 y 1440 px. Las simulaciones verifican el cliente; no demuestran entrega real de alertas ni persistencia.

Durante el desarrollo del PR no se ejecutó la demo con Docker/PostgreSQL porque el motor Docker no estaba disponible. En la integración del 13 de noviembre se ejecutaron los servicios reales: dos cuentas publicaron un hallazgo y un extravío desde el navegador, abrieron sus páginas públicas y recibieron ambas alertas. También se verificaron 20 suscriptores por HTTP; todos recibieron la alerta en 5.55 s desde la respuesta de publicación. Los detalles están en [ESTADO_02_SEPARACION.md](../../docs/ESTADO_02_SEPARACION.md).

## Demo reproducible con servicios reales

1. Preparar `.env` según `.env.example`, con los secretos locales de ambos procesos. Ejecutar `docker compose up --build -d` sin borrar volúmenes. Comprobar `/health/ready` en los puertos 8000 y 8001.
2. Crear cuenta A desde `/comunidad`, entrar y seguir Coyoacán.
3. En otra sesión independiente crear cuenta B. Publicar extravío desde `/` y hallazgo desde `/comunidad` en Coyoacán. Revisar enlaces públicos y filtro sin sesión.
4. Comprobar una alerta por reporte nuevo en A. Anotar tiempos de publicación y aparición; repetir con hasta 20 suscriptores para medir el objetivo del curso.
5. Publicar con y sin consentimiento; revisar presencia y ausencia del teléfono.
6. Simular respuesta perdida después de aceptar el reporte, reintentar sin editar y comprobar misma clave y mismo ID. Editar debe generar otra clave. Repetir con ambos tipos.
7. Detener solo `alertas`, publicar y abrir el reporte. Reiniciar `alertas` y verificar recuperación sin duplicados. Reiniciar contenedores y comprobar persistencia.
8. Dejar de seguir un municipio, cerrar sesión y verificar limpieza de datos privados. Probar token vencido y estados vacíos.
9. Repetir navegación y publicación a 390 y 1440 px, revisando foco y campos obligatorios.
