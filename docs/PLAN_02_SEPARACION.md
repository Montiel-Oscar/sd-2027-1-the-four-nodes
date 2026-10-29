# Plan de trabajo · versión 1 distribuida (`02-separacion`)

## Resultado que debemos demostrar

Partimos del monolito funcional de `01-monolito`. En esta rama habrá **dos procesos FastAPI**: `app` (identidad, mascotas, reportes y web) y `alertas` (suscripciones, bandeja y trabajador). Cada proceso escribirá solo en su base lógica: `four_nodes` y `four_nodes_alerts` dentro de PostgreSQL. El trabajador de alertas consultará por HTTP los eventos pendientes de reportes. Publicar un extravío o hallazgo no llamará a alertas y seguirá funcionando si ese proceso está apagado. Traefik, balanceo y la separación de identidad corresponden a `03-identidad-gateway`.

Las cuatro funciones del PRD deben funcionar: registrar mascotas, publicar extravíos, publicar hallazgos y seguir un municipio para ver alertas. Esta etapa añade registro e inicio de sesión básicos. No incluye correo, notificaciones del teléfono, mapa, fotos subidas por usuarios ni despliegue público.

## Reparto: cuatro ramas que parten de `02-separacion`

| Integrante | Rama y propiedad principal | Entrega verificable |
|---|---|---|
| **1. Oscar Iván Montiel Juárez** | `trabajo/oscar-reportes-v1`; `app/reports/` y sus pruebas | Hallazgos públicos, filtros por municipio, publicación idempotente, eventos pendientes de ambos tipos y API interna para consultar/confirmar eventos. No escribe en la base de alertas. |
| **2. Luisa María Segura Cedeño** | `trabajo/luisa-alertas-v1`; `app/alerts/`, `compose.yaml`, inicialización de la segunda base y sus pruebas | Proceso separado de alertas, suscripciones, bandeja, trabajador HTTP, deduplicación por evento y destinatario, recuperación tras caída. Retira el router de alertas de `app/main.py` y su importación de la metadata de reportes. |
| **3. Cecilia Ximena Solís Cisneros** | `trabajo/ceci-identidad-v1`; `app/identity/`, `app/core/auth.py` y sus pruebas | Registro con correo y contraseña con hash, inicio de sesión, token firmado, `get_actor_id` que valide Bearer sin consultar la base en cada petición. El mismo verificador funciona en ambos procesos. |
| **4. Amy Valentina Veraza García** | `trabajo/amy-web-v1`; `app/web/` y sus pruebas | Pantallas de registro/inicio, hallazgos, suscripción por municipio y bandeja; conserva la publicación de extravíos. Consulta la bandeja cada 30 segundos o menos con la página abierta. |

El reparto es por **archivos**, no por orden de inicio. Todos pueden programar en paralelo con [los contratos](CONTRATOS_02_SEPARACION.md). Oscar no debe cambiar `app/alerts/` ni `app/core/auth.py`; Luisa no debe cambiar `app/reports/`; Ceci no debe cambiar reportes ni alertas; Amy no debe cambiar la API. Cada integrante mantiene sus commits con su propia identidad de Git. Si una ruta o campo necesita cambiar, acuerden el contrato antes de modificarlo.

## Pasos concretos por integrante

### Oscar · reportes y outbox (`trabajo/oscar-reportes-v1`)

1. Crear `FoundPetReport` con descripción, ubicación, consentimiento de teléfono, usuario, clave de idempotencia y fecha. No exigir una mascota registrada.
2. Crear una tabla de outbox genérica para eventos nuevos de extravío y hallazgo. Mantener la tabla de eventos anterior y ofrecer también sus pendientes, porque `create_all` no migra ni borra tablas existentes.
3. Cambiar la publicación de extravíos para confirmar reporte y evento genérico juntos. Añadir publicación y consulta de hallazgos, con el mismo tratamiento de reintentos y conflictos.
4. Añadir listas públicas de ambos tipos, con filtro por municipio y máximo de 100 elementos. Nunca exponer `owner_id`, clave de idempotencia ni hash de la solicitud.
5. Añadir feed y ACK internos protegidos con `X-Internal-Token`; comparar el secreto de forma segura y fallar cerrado cuando falte la configuración. El feed ordena eventos pendientes y el ACK repetido no duplica efectos.
6. Probar transacción, reintento, privacidad, filtros, eventos antiguos y ACK. Verificar al menos una publicación y ACK sobre PostgreSQL. El PR de Oscar es [#4](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/4).

### Luisa · proceso de alertas (`trabajo/luisa-alertas-v1`)

1. Crear `app/alerts/main.py`, base ORM propia y modelos de suscripción y alerta. La restricción única `(event_id, recipient_id)` debe vivir en PostgreSQL. No importar `app.core.db.Base` en los modelos de alertas: eso crearía tablas en la base equivocada.
2. Implementar las rutas de suscribir, listar, cancelar y consultar bandeja del [contrato](CONTRATOS_02_SEPARACION.md#alertas-luisa--amy). Usar el UUID de `get_actor_id`; cada persona solo ve sus datos. No copiar cuentas a la base de alertas.
3. Implementar un trabajador que cada 10 s consulte `http://app:8000/api/reportes/internal/events?limit=50` con `X-Internal-Token` y timeout de 2 s. Por cada evento, guardar alertas para suscriptores ya existentes al `created_at` del evento, confirmar la transacción propia y **después** enviar ACK. Si GET o ACK falla, reintentar en el siguiente ciclo sin borrar datos.
4. Modificar Compose para levantar `alertas` como proceso separado en el puerto local 8001 y crear `four_nodes_alerts` dentro del PostgreSQL existente. La creación debe ser idempotente incluso con un volumen previo de `01-monolito`; no pedir `docker compose down -v`. Configurar `INTERNAL_API_TOKEN` en ambos procesos y `AUTH_SECRET` en ambos.
5. Quitar el router de alertas de `app/main.py` y su metadata de `app/core/db.py`. Permitir CORS solo a `http://localhost:8000` para la web local. Añadir health checks para su base propia.
6. Probar usuario ajeno, suscripción repetida, suscripción posterior al evento, entrega duplicada, caída de reportes y caída/reinicio de alertas. Documentar los comandos y el tiempo observado en su PR.

### Ceci · identidad (`trabajo/ceci-identidad-v1`)

1. Crear modelo de usuario en `app/identity/models.py` con UUID, correo normalizado y único, hash de contraseña y fecha de alta. La base sigue siendo `four_nodes` del proceso `app`.
2. Implementar registro e inicio de sesión con los cuerpos y errores del [contrato](CONTRATOS_02_SEPARACION.md#identidad-ceci--oscar-luisa-y-amy). Usar `pwdlib` con Argon2id para el hash; nunca guardar ni devolver contraseñas sin hash.
3. Emitir JWT HS256 de 60 min con `sub` UUID, `iss=the-four-nodes` y `exp`; `AUTH_SECRET` proviene solo del entorno. En `app/core/auth.py`, verificar firma, emisor y vencimiento y conservar la función `get_actor_id` para no cambiar los módulos consumidores.
4. `GET /api/usuarios/me` devuelve el ID y correo de la cuenta del token. Si falta Bearer o es inválido/vencido, devolver 401. El verificador no debe depender de consultar la base; Luisa lo reutilizará en el proceso de alertas.
5. Añadir pruebas de correo duplicado, clave incorrecta, hash distinto al texto claro, token alterado/vencido y acceso a mascota/reporte solo como su dueño. Las pruebas previas del actor demo necesitan reemplazar la dependencia en el entorno de test.
6. Documentar en el PR cómo generar `AUTH_SECRET` localmente y cómo el servicio de alertas valida el mismo token. No separar identidad en otro proceso todavía.

### Amy · interfaz (`trabajo/amy-interfaz-v1`)

1. Mantener el formulario de extravío y su reintento con la misma clave. Crear formularios de registro e inicio de sesión; conservar el token solo durante la sesión del navegador y enviarlo como Bearer en operaciones privadas.
2. Añadir formulario de hallazgo con descripción, fecha, municipio, colonia y referencia. Reutilizar el componente de consentimiento del teléfono. Crear la página pública `/reportes/hallazgos/{id}` que consulta `GET /api/reportes/hallazgos/{id}`.
3. Mostrar listas públicas filtrables por municipio para extravíos y hallazgos; cada tarjeta enlaza a la página correspondiente.
4. Añadir pantalla para seguir/dejar de seguir un municipio y bandeja de alertas. Llamar al servicio local de alertas en `localhost:8001` con Bearer y consultar la bandeja al menos cada 30 s cuando esté abierta. Los `public_url` de alertas son rutas relativas al origen de la web.
5. Mostrar estados claros para 401 (entrar), 409 (clave reutilizada con otros datos), red caída, publicación exitosa y bandeja vacía. No afirmar que se envían notificaciones al teléfono.
6. Probar manualmente en móvil y escritorio; añadir pruebas para rutas HTML y, si es posible, la lógica de envío de token y reutilización de clave. Documentar capturas o pasos reproducibles en su PR.

## Secuencia de integración

1. Publicar esta rama base con los contratos y arrancar las cuatro ramas personales desde ella.
2. Oscar entrega la API de reportes; Luisa puede desarrollar contra el JSON de ejemplo y luego probar la API real. Amy puede crear sus pantallas contra las rutas acordadas. Ceci puede cambiar la dependencia de identidad sin modificar los módulos consumidores.
3. Integrar PRs hacia **`02-separacion`**, nunca hacia `main` ni `01-monolito`. Se revisa una integración por vez. Orden práctico: Oscar → Luisa → Ceci → Amy. El desarrollo es paralelo; este orden solo reduce conflictos y permite probar cada frontera. Tras cada merge, los demás actualizan su rama desde `02-separacion`.
4. Al integrar Ceci, adaptar las pruebas que antes usaban la cuenta demo mediante `dependency_overrides[get_actor_id]` o creando un usuario de prueba. Al integrar Amy, verificar que todas las solicitudes privadas envíen `Authorization: Bearer <token>`.
5. Oscar coordina la prueba completa y documenta resultados en el README. La rama se considera lista solo cuando pasan los escenarios de abajo. Entonces se puede incorporar a `main` como versión estable.

## Pruebas de aceptación de la versión 1

1. `docker compose up --build` levanta PostgreSQL, `app` y `alertas`. `GET /health/ready` de ambos procesos responde 200. El arranque repetido no elimina datos.
2. Registrar dos usuarios, iniciar sesión y comprobar que una mascota del usuario A no aparece como propia del usuario B. Sin token, las rutas privadas devuelven 401; las páginas de reportes públicos siguen abiertas.
3. Publicar un extravío con mascota nueva y otro con mascota existente. Repetir cada `POST` con su misma `Idempotency-Key`: mismo ID, un reporte y un evento. Cambiar el cuerpo con esa clave: 409.
4. Publicar un hallazgo sin mascota registrada; consultar su enlace y filtrar extravíos/hallazgos por municipio. El teléfono aparece solo con `show_phone: true`.
5. Usuario B sigue un municipio. Publicar un reporte nuevo en ese municipio; su bandeja recibe una alerta en menos de 2 min 30 s y la página abierta la muestra en menos de 3 min, con hasta 20 suscriptores y servicios saludables. Una suscripción posterior al evento no recibe ese evento antiguo.
6. Detener solo `alertas`, publicar otro reporte y comprobar que responde 201 y su página pública carga. Reiniciar `alertas`; aparece **una sola** alerta por evento y destinatario, aunque el trabajador vuelva a recibir el mismo evento o falle la confirmación.
7. Reiniciar los contenedores y confirmar que cuentas, reportes, suscripciones y bandeja persisten. La base de reportes no contiene tablas de alertas nuevas y alertas no escribe tablas de reportes.

## Riesgos y decisiones cerradas

- La base PostgreSQL es una instancia única y puede tumbar ambos procesos. No se promete alta disponibilidad en esta etapa.
- El trabajador se ejecuta en una sola copia de `alertas` durante esta versión. Consulta cada 10 segundos, limita cada lote a 50 eventos y usa timeout de 2 segundos. Un fallo de red deja el evento pendiente para el siguiente intento.
- El ACK ocurre **después** de confirmar alertas en su base. Si se pierde el ACK, la restricción única `(event_id, recipient_id)` evita duplicar alertas visibles. No hay transacción entre las dos bases.
- Los eventos del monolito anterior se conservan y también se ofrecen al trabajador; las nuevas publicaciones usan una tabla de eventos genérica. No se borra el volumen para migrar.
- El sitio usa `localhost:8000` para reportes/identidad y `localhost:8001` para alertas durante la demo local. Luisa permite CORS únicamente al origen de la web. Traefik unificará la entrada en la siguiente etapa.
