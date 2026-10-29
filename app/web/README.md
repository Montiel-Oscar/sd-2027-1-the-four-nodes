# Amy · interfaz de extravíos

Rama: `trabajo/amy-web`, creada desde `01-monolito`.

## Implementado

- `/`: formulario en español adaptable a móvil para crear mascota y reporte juntos.
- `/reportes/extravios/{id}`: página pública que consulta la API y presenta mascota, ubicación, fecha y teléfono público cuando existe.
- Validación de campos obligatorios y longitudes según el esquema de Oscar. Fecha local convertida a ISO 8601 con zona horaria.
- Teléfono enviado únicamente con consentimiento explícito.
- Clave `Idempotency-Key` conservada al reintentar el mismo contenido tras un fallo, mientras la página permanezca abierta. Cambiar el contenido genera otro intento; recargar la página también.
- Botón deshabilitado durante el envío, errores de API/red y enlace compartible con opción de copiar.
- Datos de API insertados con `textContent` para evitar interpretar HTML.

La respuesta actual de Oscar usa `public_url` para la API JSON. La web construye el enlace de presentación desde `id`, en el mismo origen. No se modificó el contrato ni el módulo de reportes. Se priorizó crear mascota en el formulario, como permite el reparto; no se incluyó selector de mascotas existentes.

## Verificación realizada

- `python -m pytest app/web/tests -q`: 2 pruebas aprobadas (formulario, recursos y UUID de la página pública).
- `Get-Content -Raw app/web/static/app.js | node --check`: sintaxis válida.
- `docker compose config --quiet`: configuración válida usando copia local de `.env.example`.

No se verificó el flujo completo en navegador ni la persistencia: esta base aún tiene el router de reportes vacío y el motor Docker no está disponible en esta sesión.

## Prueba manual pendiente de integración

1. Integrar identidad, mascotas y reportes en `01-monolito`; incorporar esta rama.
2. Copiar `.env.example` a `.env` si no existe y ejecutar `docker compose up --build`.
3. Abrir `http://localhost:8000/` en computadora y con ancho móvil. Enviar campos vacíos y comprobar validación.
4. Publicar mascota, fecha y ubicación sin compartir teléfono. Abrir el enlace obtenido: deben aparecer los datos y no el teléfono.
5. Repetir con consentimiento y teléfono. Comprobar su aparición pública y copiar el enlace.
6. Simular pérdida de respuesta con herramientas del navegador y reintentar sin editar: comprobar la misma cabecera `Idempotency-Key` y el mismo ID. Editar datos debe crear otra clave.
7. Abrir un UUID inexistente y comprobar el error; reiniciar contenedores y verificar que el enlace publicado siga funcionando.

Para entregar, publicar `trabajo/amy-web` y abrir una solicitud hacia `01-monolito` para revisión del equipo.

## Actualización visual: fotografías y reporte guiado

La portada utiliza fotografías ilustrativas guardadas en `static/photos/`, descargadas de Unsplash:
- `golden.jpg`: archivo de origen https://images.unsplash.com/photo-1552053831-71594a27632d.
- `dog.jpg`: archivo de origen https://images.unsplash.com/photo-1587300003388-59208cc962cb.

Son imágenes de ambientación; no representan mascotas reportadas. No hay carga de fotos ni cambios al contrato de API.

El formulario tiene cuatro pasos, validación por etapa, selección visual de especie, consejos, progreso y vista previa. Las animaciones respetan `prefers-reduced-motion`.

Verificación con Edge/Playwright: fotografías cargadas, sin desbordamiento en 390/768/1440 px, campos obligatorios por paso, consentimiento de teléfono, vista previa y reintento simulado conservando la clave de idempotencia. Dos pruebas de rutas web aprobadas.

## Trabajo de Amy en `02-separacion`

Crea `trabajo/amy-interfaz-v1` desde `02-separacion`. Conserva el flujo de extravío y agrega registro/login, hallazgos, listas por municipio, suscripción y bandeja. La página HTML `/reportes/hallazgos/{id}` completa el enlace que devuelve la API de Oscar. Envía Bearer a las rutas privadas; durante esta demo local la web usa `localhost:8000` y alertas `localhost:8001`. Consulta la bandeja cada 30 segundos o menos mientras esté abierta. Sigue [PLAN_02_SEPARACION.md](../../docs/PLAN_02_SEPARACION.md#amy--interfaz-trabajoamy-interfaz-v1) y [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md). Publica PR con base `02-separacion` y documenta pruebas de móvil, errores y reintentos.

