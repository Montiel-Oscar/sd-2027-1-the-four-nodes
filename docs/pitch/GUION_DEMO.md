# Demo y pitch · The Four Nodes

Preparación de Amy, 15 de noviembre de 2026. Ensayar el tiempo que confirme el profesor: la rúbrica no especifica minutos. Este guion propone una versión de **5 minutos** con intervenciones de los cuatro; recortar o ampliar en el ensayo, sin omitir integrantes.

Abrir [diapositivas.html](diapositivas.html) en un navegador; flechas para avanzar, Inicio para volver al principio, `F11` para pantalla completa. `diapositivas.pdf` es el respaldo imprimible. No depende de Internet ni de librerías externas.

## Preparación, antes de presentar

1. Desde la raíz del repo, seguir exclusivamente el README: preparar secretos locales y `docker compose up --build -d`. No borrar volúmenes. Abrir `http://localhost:8000/` y comprobar disponibilidad. Los puertos temporales no se usan desde la web.
2. Preparar dos perfiles de navegador independientes, A (dueño) y B (vecino). No duplicar una pestaña autenticada: podría copiar su `sessionStorage`. Crear cuentas de demo sin datos personales, con contraseñas locales que no se publiquen ni aparezcan en las diapositivas.
3. Elegir un municipio de ensayo distinto cada vez, por ejemplo «Demo 15 Nov 1030». B lo sigue **antes** de publicar, desde `/comunidad#alerts`. Verificar que la bandeja del municipio nuevo esté vacía.
4. A registra «Luna» desde `/comunidad#pets`, sin crear reporte. Confirmar su ficha y que B no la ve como propia. Mantener ambas ventanas abiertas, con zoom 100 %. Preparar también emulación a 390 px.
5. Tener una ficha nueva y ambos tipos de reporte del ensayo anterior como respaldo. Comprobar sus enlaces públicos sin sesión. Registrar cuáles son capturas de API real y cuáles de pruebas locales.
6. Abrir el PDF de slides y las capturas locales antes del pitch. Confirmar cámara, compartir pantalla y reparto de voces. El PDF final del equipo es `docs/reporte-final.pdf`, que recopila Oscar; estas slides no lo sustituyen.

## Intervenciones · objetivo de 5 minutos

| Tiempo | Persona | Mensaje y acción |
|---|---|---|
| 0:00–0:40 | Amy | «Cuando se pierde una mascota, la información queda dispersa. The Four Nodes reúne fichas, extravíos, hallazgos y una bandeja por municipio. El dueño publica y comparte; el vecino ayuda sin necesitar ser dueño de esa mascota». Mostrar problema y recorrido. |
| 0:40–1:30 | Oscar | Mostrar entrada única Traefik y dos réplicas de reportes. «La web usa un solo origen. Las réplicas comparten datos; una petición puede llegar a cualquiera. El estado del intento viaja en una clave para que un reintento no cree otro reporte». Mostrar solo la arquitectura realmente integrada. |
| 1:30–2:15 | Ceci | «El login entrega un JWT firmado. Cada servicio verifica firma y vencimiento localmente. Con un token vigente, publicar no depende de consultar identidad en ese instante». Explicar que una caída de identidad sí impide registro/login. Aclarar si su separación y migración ya están integradas. |
| 2:15–3:00 | Luisa | «Reporte y evento se confirman juntos. Alertas consulta eventos y confirma después de guardar su propia transacción. Si se pierde el ACK, puede recibir el evento otra vez y la restricción por evento y destinatario evita otra alerta visible». Mostrar tabla de resultados reales; no inventar tiempos. |
| 3:00–4:40 | Amy, con apoyo del equipo | Ejecutar el recorrido siguiente. Los datos de ubicación son de demo. |
| 4:40–5:00 | Amy | «El límite es que una instancia PostgreSQL sigue siendo un punto de falla. La bandeja tiene consistencia eventual. No enviamos mensajes al teléfono ni tenemos mapa o carga de fotos». Indicar los resultados medidos y los pendientes que sigan vigentes. |

## Recorrido de pantalla · 100 segundos

1. **Ficha separada y reutilización (20 s):** mostrar «Luna» en A, elegir «Publicar extravío de esta mascota». La primera etapa muestra la ficha elegida, sin pedir capturar todo otra vez. B no la tiene en «Mis mascotas».
2. **Publicar y compartir (25 s):** completar fecha, municipio, colonia y referencia pública. Dejar teléfono sin consentimiento. Revisar y publicar. Abrir el enlace público sin sesión y copiarlo; no debe aparecer teléfono. La ruta alternativa «Crear mascota junto con el reporte» se enseña brevemente o en el respaldo.
3. **Hallazgo (20 s):** B publica un hallazgo sin ficha; usar una descripción y el mismo municipio. Puede mostrarse consentimiento con un número ficticio previamente acordado. Abrir su página pública.
4. **Descubrimiento y bandeja (25 s):** filtrar ambos reportes por el municipio. Volver a B y actualizar la bandeja. Si aún no llega el evento, continuar con la explicación y regresar; no prometer entrega instantánea. La consulta automática ocurre cada 30 s cuando la página es visible.
5. **Privacidad y móvil (10 s):** cerrar sesión; desaparecen fichas, suscripciones y bandeja. Mostrar emulación a 390 px ya preparada.

## Respaldo si falla la demo

- Si falla Internet pero los contenedores locales siguen activos, la demo local no necesita Internet. No recargar dependencias remotas: las slides son locales.
- Si falla un servicio, nombrar qué falló y qué operaciones se esperan disponibles. No presentar una captura como una petición que acaba de funcionar.
- Abrir `diapositivas.pdf` y `capturas/`. Narrar los mismos pasos y señalar el entorno de cada captura. Las capturas de la prueba local no demuestran balanceo, persistencia en PostgreSQL ni tiempos de producción.
- No detener PostgreSQL ni una réplica durante el pitch sin haber ensayado la recuperación. Oscar y Luisa muestran su evidencia reproducible o ejecutan una variante extendida si el profesor asigna tiempo.
- Un 401 requiere volver a entrar; los campos siguen abiertos. Un fallo de publicación se reintenta sin editar para conservar la clave. Una ficha independiente no tiene clave de idempotencia: si se pierde la respuesta, actualizar «Mis mascotas» antes de repetir.

## Preguntas cruzadas para el ensayo

- ¿Qué partes recorre una petición y dónde se guarda cada dato?
- ¿Por qué no hacemos una llamada sincrónica a alertas dentro de publicar?
- ¿Qué pasa si se guarda la alerta pero no llega el ACK?
- ¿Cómo saben las dos réplicas que un reintento es el mismo intento?
- ¿Por qué el usuario B no puede publicar con el `pet_id` de A aunque modifique el navegador?
- ¿Por qué una suscripción nueva no recibe reportes anteriores?
- ¿Qué cambia si expira el token? ¿Qué se conserva al recargar la página?
- ¿Qué fallas siguen afectando a todos? ¿Qué afirmaciones tienen evidencia medida?
