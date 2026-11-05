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

## Configuración local

1. Copiar `.env.example` a `.env` si aún no existe. Conservar la contraseña de
   PostgreSQL existente para reutilizar el volumen.
2. Generar un secreto con Python:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. Pegar el resultado en `.env` como `AUTH_SECRET=valor_generado`. Debe tener
   al menos 32 bytes. No subir `.env`, no pegar el secreto en el PR.
4. Ejecutar `docker compose up --build -d` y abrir `http://localhost:8000/docs`.

La tabla de usuarios se crea durante el arranque con la metadata existente.
No se necesita borrar el volumen. Las mascotas/reportes de la cuenta demo
anterior conservan su dueño original; no se asignan automáticamente a cuentas
nuevas.

## Comprobar registro e inicio de sesión

En `/docs`, ejecutar:

1. `POST /api/usuarios/register` con
   `{"email":"persona@example.org","password":"una-clave-de-8-o-mas"}`.
   Devuelve 201 con `id` y correo. Repetir el correo, incluso cambiando sus
   mayúsculas, devuelve 409. Un correo inválido o contraseña fuera de 8–1024
   caracteres devuelve 422. La contraseña no se recorta ni cambia de caso.
2. `POST /api/usuarios/login` con los mismos datos. Devuelve `access_token`
   y `token_type: bearer`. Credenciales incorrectas devuelven 401.
3. Pulsar **Authorize** y pegar únicamente el token en el campo de HTTPBearer.
4. `GET /api/usuarios/me` devuelve el ID y correo de la cuenta.
5. Crear una mascota y publicar un extravío con esa ficha. Con otra cuenta,
   esa mascota no aparece en la lista propia y consultarla devuelve 404.
6. Sin token, o con uno inválido/vencido, las rutas privadas devuelven 401 y
   `WWW-Authenticate: Bearer`. Los reportes públicos continúan accesibles.
7. Reiniciar con `docker compose restart`; iniciar sesión de nuevo y comprobar
   que la cuenta, mascotas y reportes siguen guardados.

Si `AUTH_SECRET` falta o tiene menos de 32 bytes, la emisión o comprobación de
un token responde 503: no se utiliza un secreto por defecto.

## Integración con alertas

Luisa debe pasar **el mismo `AUTH_SECRET`** al proceso `alertas` y reutilizar
`Depends(get_actor_id)` de `app.core.auth`. Ese módulo solo requiere FastAPI,
PyJWT y el secreto; no necesita la base de identidad ni llamadas HTTP a `app`.
El token emitido por login sirve en ambos procesos. Las cuentas se guardan
únicamente en `four_nodes`. Cambiar el secreto invalida los tokens anteriores.

Este PR solo incorpora la variable en el servicio `app`; al integrar la rama
de alertas, su Compose también debe transmitirla al nuevo servicio. No crea
el trabajador, las suscripciones ni las pantallas de login.

## Pruebas

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

`tests/test_identity.py` comprueba registro, normalización/unicidad, Argon2id,
credenciales incorrectas, respuestas sin contraseñas, expiración, alteración,
firma/emisor/algoritmo/claims inválidos, configuración ausente y aislamiento
entre dos usuarios. También valida el mismo token en otra app FastAPI sin
sesión de base de datos, para comprobar su uso por alertas.

Las pruebas rápidas usan SQLite en memoria; el esquema de prueba adapta los
UUID de PostgreSQL a CHAR para evitar conversiones numéricas de SQLite.
La validación con Docker utiliza PostgreSQL y conserva el volumen anterior.

## Resultado de verificación

- **30 pruebas aprobadas** en la suite completa.
- Docker Compose y PostgreSQL: registro de dos cuentas, correo duplicado,
  contraseña incorrecta, login, `/me`, acceso privado y propiedad de mascotas.
- Comprobación directa de hashes Argon2id y `owner_id` en PostgreSQL.
- Publicación y reintento de extravío con Bearer; consulta pública sin token.
- Token validado desde un segundo contenedor sin conexión a la base de usuarios.
- Reinicio de app y PostgreSQL: cuenta, contraseña protegida, login, token,
  mascota y reporte conservados. Volumen previo del monolito preservado.

La integración completa con el servicio de alertas y las pantallas se verifica
cuando se incorporen las ramas de Luisa y Amy.
