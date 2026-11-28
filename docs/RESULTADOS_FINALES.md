# Resultados de la entrega final · 26 de noviembre de 2026

## Alcance y entorno

Ensayos locales con Docker Compose, una instancia PostgreSQL con tres bases lógicas, Traefik, dos réplicas de reportes, identidad y alertas. Luisa preparó el script de 20 suscriptores y el análisis del outbox; Oscar corrigió el contrato del extravío, el nombre del contenedor de base y ejecutó los ensayos tras integrar el PR #20. Se usaron cuentas y municipios de prueba nuevos en cada repetición. Los tiempos se miden desde la respuesta HTTP de publicación hasta la observación de la alerta en la bandeja por API; **no** miden el tiempo hasta que una persona la ve en pantalla.

## Funcionalidad y autorización

`PUT /api/mascotas/{pet_id}` permite editar nombre, especie y rasgos solo al dueño; otro usuario recibe 404. El reporte publicado guarda una instantánea descriptiva, por lo que la edición posterior de la ficha no modifica el enlace ya compartido. La suite Python pasó **41 pruebas**. La prueba de navegador con dos cuentas confirmó que se puede marcar un punto en extravío y hallazgo y que los enlaces públicos muestran el mapa. Las coordenadas de reportes anteriores son opcionales y siguen disponibles sus ubicaciones escritas. La ruta de identidad ya vive en el proceso `identidad` y su propia base lógica; `reportes_a`, `reportes_b` y `alertas` verifican JWT localmente.

## Contacto privado sin teléfono

Una persona autenticada puede escribir desde el enlace público de un reporte; el autor ve la conversación en **Comunidad → Mensajes** y puede responder. La conversación y sus mensajes se guardan en la base de reportes. Sólo el autor y quien inició el contacto pueden leer o escribir en ella. `scripts/smoke_contact.py` confirmó envío, respuesta, ausencia de teléfono y rechazo a una tercera cuenta a través de Traefik. La interfaz se comprobó en el navegador con registro, envío y lectura. Los mensajes se consultan cada 30 segundos mientras la página está visible; no hay notificación fuera de la aplicación.

## Interfaz y fotografía opcional

El registro usa una pantalla separada y regresa al inicio de sesión tras crear la cuenta. Al entrar, la persona vuelve a la sección desde la que llegó y ve una indicación de sesión activa. La comunidad presenta una sección por vez y accesos directos a fichas, extravíos, hallazgos, reportes, mensajes y alertas. Un ensayo HTTP a través de Traefik confirmó que una foto JPG se guarda y puede leerse tras varias solicitudes, con ambas réplicas de reportes activas. La prueba automatizada también verifica tipo, tamaño y autorización para reemplazarla. Las siluetas se usan cuando no hay foto. Esta prueba no mide rendimiento de imágenes bajo carga.

## Entrega con 20 suscriptores

Las mediciones siguientes se hicieron antes de añadir el mapa; el script de API sigue enviando ubicación textual. La incorporación del mapa se verificó por separado y no se presenta como una nueva medición de latencia.

Tras integrar el mapa se repitió un ensayo con **20 suscriptores**, sin coordenadas en el script de API: hallazgo 20/20 en **9.170 s** y extravío 20/20 en **9.798 s**, sin alertas duplicadas. Esto verifica compatibilidad del flujo de alertas; no mide la carga de teselas ni la interacción humana con el mapa.

Comando reproducible:

```bash
python3 scripts/resilience_20_subscribers.py --subscribers 20 --trials 3 --timeout 150 --with-faults
```

| Ensayo | Hallazgo: POST (s) | Hallazgo: primera / todas (s) | Extravío: POST (s) | Extravío: primera / todas (s) |
|---|---:|---:|---:|---:|
| 1 | 0.006 | 8.573 / 9.147 | 0.025 | 9.751 / 9.806 |
| 2 | 0.006 | 6.876 / 7.442 | 0.020 | 9.684 / 9.744 |
| 3 | 0.006 | 7.383 / 7.439 | 0.007 | 10.244 / 10.307 |

En los seis reportes, **20 de 20 suscriptores** recibieron exactamente una alerta cada uno. El tiempo máximo hasta consultar las 20 alertas fue **10.307 s**, por debajo del objetivo de tres minutos en este entorno local. La muestra es pequeña: no establece una garantía de servicio para Internet o cargas mayores. La página web consulta la bandeja periódicamente, por lo que su visualización puede tardar más que la creación en la base.

## Fallas observadas

- **Alertas detenidas:** un hallazgo se publicó con HTTP 201. Al reiniciar `alertas`, la cuenta suscrita recibió una sola alerta; el script la observó **2.518 s** después de volver a consultar. El evento quedó pendiente mientras el servicio estuvo detenido.
- **PostgreSQL detenido:** la publicación devolvió HTTP 500, no 201. El servicio se reinició sin borrar el volumen. El script comprueba que el intento fallido no aparezca en la lista al recuperarse.
- **Una réplica de reportes detenida:** `scripts/verify_gateway.py` completó el registro, hallazgo, entrega de alerta y bandeja con `reportes_b` mientras `reportes_a` estaba detenida; después reinició la primera. Traefik necesita unos segundos para detectar una caída y puede responder 502 en ese intervalo.
- **Identidad detenida:** el JWT vigente puede seguir autorizando publicación porque reportes verifica la firma localmente. Registro y login dependen de identidad. Esta condición se comprueba por separado en la verificación final.

## Decisión: outbox y ACK

El reporte y el evento pendiente se confirman en una transacción local. El trabajador de alertas lee el evento por HTTP interno, guarda las alertas y después envía ACK. Se descartó enviar alertas sincrónicamente dentro del POST de publicación: una falla del servicio de alertas habría impedido guardar un reporte válido. También se descartó confirmar el evento antes de guardar las alertas: un reinicio en ese punto habría perdido el aviso. La unicidad por evento y destinatario impide duplicados visibles si se repite el consumo.

## Límites

El ensayo no prueba despliegue público, entrega por correo o push, ni disponibilidad de la instancia PostgreSQL. Las tres bases son lógicas y comparten ese punto de falla físico. La medición observó alertas por API, no el instante en que una persona abre la bandeja. Para una versión posterior convendría medir en varias máquinas y normalizar los nombres de municipio.
