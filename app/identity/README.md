# Ceci · identidad de `02-separacion`

Rama personal: `trabajo/ceci-identidad-v1`, creada desde `02-separacion`.
El Pull Request se dirige a **`02-separacion`**.

Esta etapa sustituye la cuenta demo por cuentas reales dentro del proceso `app`
y su base `four_nodes`. El contrato está en
[CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md).
Las pantallas corresponden a Amy; el proceso de alertas corresponde a Luisa.

## Implementación

- `models.py`: tabla `users`, UUID, correo único en minúsculas, hash Argon2id
  con sal por cuenta y fecha de alta UTC. No se guardan contraseñas en claro.
- `router.py`: registro, login y cuenta actual; las respuestas excluyen hashes
  y contraseñas, incluidos los errores de validación.
- `app/core/auth.py`: emisión y verificación JWT HS256 con `sub` UUID,
  `iss=the-four-nodes` y `exp` a 60 minutos. `get_actor_id` conserva su nombre.
- La validación del token no importa modelos ni consulta la base de usuarios.
  `/me` sí consulta la cuenta para devolver el correo.
- `compose.yaml` pasa `AUTH_SECRET` del entorno al contenedor `app`.
- Las pruebas anteriores de reportes sustituyen `get_actor_id` por un actor de
  prueba. No hay acceso automático como demo en las rutas privadas reales.

Cecilia verificó el actor fijo de `app/core/auth.py` y el flujo con mascotas y reportes en la [solicitud #6](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/6). Esta cuenta de demostración es compartida por todos los visitantes locales. La autenticación real está integrada en `02-separacion` mediante la [solicitud #7](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/pull/7).

## Verificación de la entrega de identidad

El actor demo y `/api/usuarios/me` ya estaban implementados durante la integración.
Esta rama documenta su contrato y añade una prueba de integración con los routers
reales de identidad, mascotas y reportes, sin atribuirse la implementación previa.

- `DEMO_USER_ID` es un UUID fijo definido una sola vez en `app/core/auth.py`.
- `get_actor_id()` entrega ese UUID. Los endpoints privados lo reciben mediante
  `Depends(get_actor_id)` y lo guardan como `owner_id`.
- `GET /api/usuarios/me` responde con `id` y `mode: demo` sin requerir credenciales.
- No existe una tabla de cuentas para esta etapa: el actor es lógico y compartido.
  Reiniciar la aplicación no cambia su ID.

### Comprobarlo manualmente

1. Copiar `.env.example` a `.env` y ejecutar `docker compose up --build`.
2. Abrir `http://localhost:8000/docs` y ejecutar `GET /api/usuarios/me` dos veces.
   Ambas respuestas deben contener `00000000-0000-4000-8000-000000000001`.
3. Ejecutar `POST /api/mascotas` con nombre, especie y rasgos; conservar su `id`.
4. Ejecutar `GET /api/mascotas`: debe incluir la ficha creada.
5. Ejecutar `POST /api/reportes/extravios` con ese `pet_id`, una cabecera
   `Idempotency-Key` y los campos del contrato. Debe responder 201.
6. Consultar el reporte con `GET /api/reportes/extravios/{id}` sin credenciales.

### Pruebas automatizadas

Con Python 3.12 o posterior y las dependencias de desarrollo instaladas:

```powershell
python -m pip install -e '.[dev]'
python -m pytest tests/test_identity.py tests/test_identity_integration.py -q
```

La prueba de integración usa SQLite en memoria para comprobar que la mascota y
el reporte guardan el mismo dueño que devuelve identidad. También sustituye el
actor mediante `dependency_overrides[get_actor_id]`: otro actor no puede listar
ni consultar esa ficha, mientras el reporte continúa siendo público. No sustituye
la verificación manual con PostgreSQL y Docker Compose.

### Paso a autenticación real

En la siguiente entrega se conservará el nombre `get_actor_id` y su retorno UUID,
pero se obtendrá el identificador de un token validado. Los módulos consumidores
no deben importar `DEMO_USER_ID` ni aceptar un dueño enviado en el formulario.
Identidad incorporará cuentas, hashes y emisión de tokens. Las pruebas podrán
seguir sustituyendo la dependencia; las rutas públicas permanecerán públicas.

### Resultados de verificación

- Suite completa: **10 pruebas aprobadas** (`python -m pytest -q`).
- Docker Compose levanta la aplicación y PostgreSQL; `/health/ready` responde 200.
- `/api/usuarios/me` conserva el mismo UUID en solicitudes sucesivas.
- Una mascota y un extravío creados por la API guardan ese UUID como `owner_id`
  en PostgreSQL.
- Repetir la publicación con la misma clave devuelve el mismo reporte.
- Después de `docker compose restart`, la identidad, la mascota, el reporte y
  su página pública siguen disponibles.

## Siguiente entrega

En `02-separacion`, Ceci añadió registro, login y JWT. El contrato está en [CONTRATOS_02_SEPARACION.md](../../docs/CONTRATOS_02_SEPARACION.md) y el [estado de integración](https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes/blob/02-separacion/docs/ESTADO_02_SEPARACION.md) está en esa rama.
