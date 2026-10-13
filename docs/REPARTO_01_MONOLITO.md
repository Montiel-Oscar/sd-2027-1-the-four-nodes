# Reparto de la primera entrega: `01-monolito`

**Meta de la entrega:** una aplicación y una base que permitan publicar un extravío de mascota, guardar los datos, consultar el reporte por su enlace y reiniciar la aplicación sin perderlo. El PRD permite que esta rama use una cuenta de demostración. Las cuatro tareas se pueden desarrollar en paralelo **después de acordar los contratos de [CONTRATOS_01_MONOLITO.md](CONTRATOS_01_MONOLITO.md)**; la integración se hace en el orden indicado al final.

| Orden | Integrante y rama personal | Carpeta principal | Trabajo y resultado verificable |
|---|---|---|---|
| **1** | **Oscar Ivan Montiel Juarez** · `trabajo/oscar-extravios` | `app/reports/` | Implementar `POST /api/reportes/extravios` y `GET /api/reportes/extravios/{id}`; guardar reporte y evento pendiente en una transacción; admitir mascota existente o nueva; evitar duplicados con clave de idempotencia. Una prueba debe mostrar que el mismo intento devuelve el mismo ID. |
| 2 | Luisa María Segura Cedeño · `trabajo/luisa-mascotas` | `app/pets/` | Modelo y operaciones para registrar, listar y consultar mascotas del dueño; exponer una función que Oscar use para crear mascota dentro de la transacción del reporte. Probar propiedad de la ficha y reutilización. |
| 3 | Cecilia Ximena Solis Cisneros · `trabajo/cecilia-identidad` | `app/identity/` y `app/core/auth.py` | Preparar la cuenta de demostración para esta rama y la dependencia que entrega su ID a los otros módulos. Si alcanza el tiempo, añadir registro e inicio de sesión básicos sin bloquear el flujo principal. Probar que las operaciones privadas conocen al mismo usuario. |
| 4 | Amy Valentina Veraza García · `trabajo/amy-web` | `app/web/` | Formulario web adaptable a móvil para publicar extravío y página pública del reporte. Consumir los contratos acordados; mostrar errores de validación y el enlace compartible. Probar manualmente el flujo desde el navegador. |

## Dependencias e integración

El esqueleto común, Docker Compose, la base de datos y las rutas vacías ya están preparados. **Primero** Cecilia fija el ID de demostración y Luisa define el modelo y la función de creación de mascotas según el contrato. Oscar y Amy pueden comenzar sus módulos en paralelo usando ese contrato; no necesitan esperar a que los otros terminen. **Después**, se integran identidad y mascotas, luego reportes y por último la web. Oscar coordina la prueba completa; cada integrante conserva sus propios commits.

Si el tiempo no alcanza, cierren primero **publicar y consultar un extravío con mascota creada en el formulario**. La ficha reutilizable y la interfaz visual pueden simplificarse; hallazgos y bandeja de alertas pertenecen a la siguiente rama según el PRD.
