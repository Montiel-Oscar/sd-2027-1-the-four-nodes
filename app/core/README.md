# Núcleo compartido del monolito

`db.py` contiene la conexión y la metadata común; `auth.py` expone el actor de demostración. Estas piezas ya están preparadas para que los cuatro módulos trabajen en paralelo. **Cecilia** es la responsable de cambios en `auth.py`; cualquier cambio en `db.py` se acuerda antes con Oscar para evitar conflictos.

En `01-monolito` hay **una aplicación y una base**. Los modelos de cada equipo se importan en `init_db()` y la metadata crea las tablas al iniciar. Este mecanismo es suficiente para la primera entrega; al evolucionar el proyecto deberán usar migraciones controladas para cambios de esquema.
