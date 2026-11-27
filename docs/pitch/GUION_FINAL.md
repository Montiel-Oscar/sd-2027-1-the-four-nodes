# Pitch y demostración final · The Four Nodes

**Duración propuesta:** 5 minutos. La rúbrica no indica duración exacta; si el profesor asigna otra, conservar la intervención de las cuatro personas y recortar la demo. Abrir `docs/pitch/diapositivas.html` en Chrome y pulsar `F11`; se avanza con la flecha derecha. `docs/pitch/diapositivas.pdf` sirve de respaldo. Compartir la pantalla con cámara encendida.

## Qué dice cada integrante

| Tiempo | Diapositiva | Voz | Texto sugerido |
|---|---|---|---|
| 0:00–0:40 | 1–2 | **Amy** | «Cuando se pierde una mascota, la búsqueda suele depender de carteles y de preguntar cerca. La información llega a poca gente y los hallazgos quedan separados. The Four Nodes permite guardar la ficha de una mascota, publicar un extravío o hallazgo y compartir el enlace. Los vecinos pueden seguir un municipio para enterarse de reportes nuevos». |
| 0:40–1:25 | 3 | **Oscar** | «La web entra por Traefik en un solo puerto. Dos copias del servicio de reportes comparten sus datos en PostgreSQL. Si una se detiene, la otra puede seguir atendiendo; durante la detección puede haber un error transitorio, y por eso el reporte lleva una clave para reintentar sin duplicarlo. Tenemos tres bases lógicas dentro de una instancia PostgreSQL». |
| 1:25–2:05 | 4 | **Ceci** | «El usuario se registra e inicia sesión en el servicio de identidad. Recibe un token JWT firmado. Reportes y alertas comprueban el token localmente, sin llamar a identidad en cada petición. Comprobamos que, si identidad se detiene, no hay nuevo login, pero un token vigente permite publicar. Las fichas sólo se consultan y editan desde la cuenta dueña». |
| 2:05–2:50 | 5 | **Luisa** | «Al publicar, el reporte y un evento pendiente se guardan juntos. Alertas lee ese evento y confirma después de guardar cada aviso. Si se cae o se pierde la confirmación, reintenta sin mostrar alertas duplicadas. En tres ensayos locales con 20 suscriptores, todos recibieron una alerta por reporte; el mayor tiempo para consultar las 20 bandejas fue 10.307 segundos. PostgreSQL sigue siendo un punto de falla». |
| 2:50–4:40 | 6 | **Amy** | «Ahora mostramos el flujo real. La cuenta A ya tiene una ficha de Luna; la B sigue el municipio de la demo. A reutiliza la ficha y publica. El enlace abre sin iniciar sesión y no muestra teléfono porque no se autorizó. B publica un hallazgo y la bandeja recibe los reportes nuevos». Ejecutar los clics de abajo. |
| 4:40–5:00 | 7 | **Oscar** | «La versión entregada incluye cuentas, mascotas, extravíos, hallazgos, enlaces públicos, bandeja y pruebas de fallas. El mapa muestra un punto aproximado y un radio de 3 km; todavía no hay mensajes al teléfono ni alta disponibilidad de PostgreSQL. El código, las mediciones y el reporte están en el repositorio». |

No recitar la tabla de tiempos completa; mostrar el dato máximo y, si preguntan, abrir `docs/RESULTADOS_FINALES.md`.

## Preparación antes de compartir pantalla (5–10 minutos)

1. Desde la raíz del repositorio: `python3 scripts/setup_env.py` y `docker compose up --build -d`. Abrir `http://localhost:8000/health/ready` y comprobar `{"status":"ready"}`. Abrir `http://localhost:8000/` y `http://localhost:8000/comunidad`. Mantener abierta la terminal para mostrar `docker compose ps` sólo si el profesor pregunta.
2. Elegir `Cuauhtémoc`, que corresponde a la zona inicial del mapa. Usar cuentas nuevas en cada ensayo. Usar el **mismo texto exacto** en suscripción, extravío, hallazgo y filtro. Si se repite el ensayo, los reportes públicos anteriores pueden seguir visibles, pero las cuentas nuevas no reciben alertas retroactivas.
3. Preparar dos perfiles o ventanas de incógnito independientes: **A, dueño**, y **B, vecino**. En cada una, ir a `/comunidad`, llenar **Correo** y **Contraseña**, pulsar **Crear cuenta** y después **Entrar**. Usar cuentas ficticias; no mostrar contraseñas en pantalla compartida.
4. En B, dentro de **Municipios que sigues**, escribir el municipio elegido y pulsar **Seguir municipio**. Debe aparecer en la lista antes de cualquier publicación. Dejar B en `/comunidad#alerts`.
5. En A, dentro de **Mis mascotas**, llenar **Nombre: Luna**, **Especie: perro**, **Características: pelaje café, collar azul**; pulsar **Guardar ficha sin publicar**. Verificar que aparece Luna. No crear todavía un reporte.
6. Preparar el PDF de respaldo y `docs/pitch/capturas/entorno.json`. Esas capturas se generaron con APIs locales y SQLite temporal; sirven como respaldo visual, no como evidencia de la ejecución actual con PostgreSQL. Si la demo en vivo funciona, no mostrarlas.

## Clics exactos durante la demo

1. **Ficha y extravío, ventana A.** En `/comunidad#pets`, señalar la ficha Luna y hacer clic en **Publicar extravío de esta mascota**. Abre la página inicial con **Ficha de mascota: Luna** seleccionada. Señalar que nombre, especie y rasgos aparecen llenos y bloqueados: se reutiliza la ficha propia.
2. Pulsar **Continuar**. En **El último encuentro**, elegir la fecha y hora actual o reciente; escribir el municipio de demo, **Colonia: Centro** y **Punto de referencia: Entrada del parque**. Antes de continuar, mover el mapa y hacer clic en el lugar aproximado del extravío: aparecerá un punto rojo y un círculo de 3 km. Pulsar **Continuar**. En **Cómo contactarte**, dejar sin marcar **Quiero mostrar mi teléfono**. Pulsar **Continuar**. Revisar la vista previa y pulsar **Publicar y obtener mi enlace**.
3. En **Tu reporte está publicado**, hacer clic en el enlace del reporte. Abrirlo en otra ventana sin sesión o incógnito y señalar que el enlace es público, el teléfono no aparece y el mapa muestra el punto rojo con un radio de 3 km. Pulsar **Copiar enlace**. Decir: «Este enlace puede compartirse fuera de la aplicación».
4. **Hallazgo, ventana B.** Ir a `/comunidad#found`. En **Encontré una mascota**, llenar **Descripción: Perro con collar azul junto al parque**, fecha y hora actual, el mismo municipio, **Colonia: Centro** y **Referencia pública: Fuente del parque**. Dejar sin teléfono o usar un número ficticio con consentimiento explícito. Hacer clic en el mapa del hallazgo para marcar el punto. Pulsar **Publicar hallazgo**, luego **Abrir y compartir reporte**.
5. En B, ir a **Extravíos y hallazgos recientes**, poner el municipio en el filtro y pulsar **Buscar reportes**. Deben aparecer el extravío y el hallazgo. Después bajar a **Bandeja de alertas** y pulsar **Actualizar bandeja**. Si todavía no aparecen, esperar unos segundos y repetir; el trabajador revisa eventos periódicamente y la web también actualiza cada 30 segundos. Señalar que son alertas nuevas de un municipio seguido antes de publicar.
6. Si queda tiempo, pulsar **Cerrar sesión** en B y mostrar que fichas, suscripciones y bandeja privadas desaparecen. En emulación móvil de Chrome (`Ctrl+Shift+M`), elegir ancho **390 px** y mostrar que la página sigue legible.

**Variante de 90 segundos:** hacer la preparación completa antes del pitch; durante la demo mostrar solo la ficha de A, completar y publicar el extravío, abrir el enlace público y actualizar la bandeja de B. Dejar el hallazgo y la vista móvil para preguntas o para una demo extendida.

## Si algo falla

- **Un 502 breve tras detener una réplica:** esperar dos segundos y reintentar con el mismo formulario y clave automática. No volver a crear la ficha.
- **La alerta no aparece enseguida:** mostrar que el reporte ya está publicado, explicar el outbox, esperar y pulsar **Actualizar bandeja**. No decir que la entrega fue instantánea.
- **Se pierde la respuesta al registrar una ficha:** pulsar **Actualizar mis fichas** antes de repetir el alta; esa operación no usa clave de idempotencia.
- **Docker o navegador falla:** mostrar las diapositivas PDF y las capturas de respaldo, identificando su entorno. Abrir `docs/RESULTADOS_FINALES.md` para los resultados medidos; no presentar las capturas como una operación en vivo.

## Preguntas de defensa y respuestas breves

- **¿Por qué consistencia eventual?** Porque el reporte queda confirmado primero; la alerta se crea después en otra base. La bandeja converge cuando el trabajador consume el evento pendiente.
- **¿Qué pasa si alertas cae?** El reporte responde 201 y el evento queda pendiente. Al reiniciar alertas, se procesa; la unicidad evita duplicados visibles.
- **¿Qué pasa si se pierde el ACK?** El evento se vuelve a leer. La alerta ya guardada se reconoce por evento y destinatario y no se muestra dos veces.
- **¿Qué pasa si identidad cae?** No hay registro ni login; un JWT vigente sigue autorizando otras operaciones porque se verifica localmente.
- **¿Qué pasa si cae PostgreSQL?** No se confirma una publicación; la base única es un punto de falla. En el ensayo se obtuvo HTTP 500, no 201.
- **¿Por qué dos réplicas?** Traefik puede dirigir solicitudes a la réplica sana. Ambas comparten datos; la clave idempotente permite reintentar una publicación si la respuesta se perdió.
- **¿Se cumplió el objetivo de tres minutos?** En seis publicaciones locales con 20 suscriptores, sí: el máximo para consultar todas las alertas fue 10.307 s. No es garantía para Internet ni una medición de la vista abierta.
