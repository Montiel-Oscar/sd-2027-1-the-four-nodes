# Oscar · extravíos (tarea 1)

**Rama de partida:** `01-monolito`. Antes de editar: `git switch 01-monolito`, `git pull origin 01-monolito` y `git switch -c trabajo/oscar-extravios`. En GitHub Desktop, elige `01-monolito` en **Current branch**, actualízala y crea la nueva rama desde ella.

Implementa en esta carpeta el reporte de extravío, la consulta pública y el evento pendiente. Sigue el cuerpo y la respuesta de [los contratos](../../docs/CONTRATOS_01_MONOLITO.md). Para crear una mascota nueva, llama a la función de Luisa usando **la misma sesión** de SQLAlchemy. El reporte y el evento se confirman juntos; si cualquier paso falla, se revierten juntos.

**Entregable:** `POST /api/reportes/extravios` y `GET /api/reportes/extravios/{id}`; clave de idempotencia por usuario; prueba de publicación y prueba de reintento sin duplicado. El enlace público debe incluir el ID guardado. No implementes todavía la comunicación con un servicio de alertas separado.

Haz commits con tu identidad de Git, publica `trabajo/oscar-extravios` y solicita integración hacia `01-monolito`. Después de integrar identidad y mascotas, coordina una prueba del flujo completo con Amy.
