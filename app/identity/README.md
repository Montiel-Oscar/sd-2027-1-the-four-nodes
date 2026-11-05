# Cecilia · identidad de la primera entrega

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/cecilia-identidad`. En GitHub Desktop, selecciona la rama base, actualízala y crea tu rama personal.

El [PRD](../../docs/PRD.md) permite una cuenta de demostración en esta rama. Revisa `app/core/auth.py` y deja una dependencia `get_actor_id` estable para Oscar y Luisa. Si añades registro e inicio de sesión, deben seguir siendo parte de **esta única aplicación y base**; no crees otro servicio todavía.

**Entregable mínimo:** un actor de demostración consistente y una prueba que muestre que las operaciones privadas reciben su ID. Documenta cómo sustituirlo por autenticación real. Si completas registro e inicio de sesión, añade pruebas de contraseña incorrecta y de acceso sin sesión. Publica tu rama y solicita integración hacia `01-monolito`.

## Estado integrado

No se recibió una rama o solicitud de integración de Cecilia para esta etapa. Se completó el mínimo con el actor fijo de `app/core/auth.py`, `GET /api/usuarios/me` y `tests/test_identity.py`. Toda publicación y ficha usa `get_actor_id`; las cuentas reales, credenciales y tokens quedan para las ramas posteriores del PRD. Esta cuenta de demostración es compartida por todos los visitantes locales.

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
