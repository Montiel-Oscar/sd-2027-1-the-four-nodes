# Abrir y demostrar The Four Nodes: guía paso a paso

Esta guía es para quien va a manejar la computadora durante la exposición. Todo se ejecuta **en tu computadora**: la dirección `localhost:8000` no es un sitio público. Las cuentas y mascotas que crees aquí son datos de ensayo y permanecen en el volumen local de PostgreSQL. Usa nombres, correos y teléfonos ficticios.

## 1. Encender la aplicación

Abre **una terminal**. Copia estos comandos, uno por uno:

```bash
cd /home/ivan/Documents/FI/sd-2027-1-the-four-nodes
python3 scripts/setup_env.py
docker compose up --build -d
docker compose ps
```

Qué significa cada línea:

1. `cd` entra en la carpeta del proyecto. Si la clonaste en otra ubicación, usa esa carpeta.
2. `setup_env.py` crea `.env` con claves locales si no existe. Si ya existe, conserva las claves y las cuentas anteriores. **No muestres ni subas `.env`.**
3. `docker compose up --build -d` construye e inicia los servicios en segundo plano. La primera vez puede tardar unos minutos. Deja esta terminal abierta.
4. `docker compose ps` muestra los contenedores. Deben estar funcionando `db`, `identidad`, `reportes_a`, `reportes_b`, `alertas` y `gateway`. Los contenedores de inicialización pueden aparecer como terminados: eso es normal.

Si Docker dice que no puede conectarse al daemon, abre Docker Desktop y espera a que termine de iniciar; después repite el tercer comando. **No ejecutes `docker compose down --volumes`**: eso borraría las cuentas y reportes de ensayo.

En el navegador abre <http://localhost:8000/health/ready>. Debe aparecer `{"status":"ready"}`. Si acabas de iniciar los contenedores y aún no aparece, espera unos segundos y recarga. Luego abre <http://localhost:8000/>: esa es la aplicación.

## 2. ¿Cuántas pestañas necesito?

Prepara **cuatro pestañas** del navegador y una terminal. Se pueden abrir todas en Chrome. Crea cada pestaña con `Ctrl+T`; **no uses “Duplicar pestaña”**, porque la sesión puede copiarse. La aplicación guarda el inicio de sesión por pestaña.

| Pestaña | Dirección | Para qué sirve | Quién inicia sesión |
|---|---|---|---|
| **1. Diapositivas** | Abre `docs/pitch/diapositivas.html` desde el explorador de archivos | Presentar el problema y la arquitectura. `F11` pone pantalla completa; flechas cambian de diapositiva. | Nadie |
| **2. Dueño A** | <http://localhost:8000/comunidad> | Crear la ficha de Luna y publicar el extravío. Después navegarás a `/` **en esta misma pestaña**. | Cuenta A |
| **3. Vecino B** | <http://localhost:8000/comunidad> | Seguir un municipio, publicar un hallazgo, buscar reportes y revisar la bandeja. | Cuenta B, distinta de A |
| **4. Público** | Déjala en blanco hasta copiar el enlace de un reporte | Abrir el enlace pegándolo en la barra de direcciones y demostrar que se ve sin iniciar sesión. | Nadie |

La pestaña **Público** debe ser una pestaña nueva, abierta con `Ctrl+T`. No pulses “Duplicar” sobre la pestaña A. Si quieres una separación aún más visible, usa una ventana de invitado o incógnito para Público. No cierres A ni B al mostrar el enlace.

**Antes de compartir pantalla**, deja la terminal y las cuatro pestañas preparadas. Durante el pitch alternarás entre diapositivas, A, B y Público. La terminal sólo se muestra si te preguntan cómo se levantó el sistema.

## 3. Elegir datos de ensayo

Usa **Cuauhtémoc** como alcaldía de ensayo: el mapa inicial muestra esa zona de Ciudad de México. Escríbelo exactamente igual en la suscripción, los reportes y el filtro. Si repites la demostración, crea cuentas de ensayo nuevas para que su bandeja empiece vacía; en la lista pública pueden quedar reportes de prácticas anteriores.

Ejemplo de cuentas ficticias:

- **A:** `dueno.demo.26a@example.org`
- **B:** `vecino.demo.26a@example.org`

Elige una contraseña de al menos 8 caracteres para cada cuenta. Guárdala para el ensayo, pero no la digas ni la muestres al compartir pantalla. Si esos correos ya existen, pulsa **Entrar** o usa otros correos de ensayo.

## 4. Preparación de A y B antes de comenzar a hablar

### Pestaña A: registrar e iniciar sesión

1. Ve a <http://localhost:8000/comunidad>.
2. En **Entrar o crear una cuenta**, escribe el correo de A y su contraseña.
3. Pulsa **Crear cuenta**. Debe decir **“Cuenta creada. Inicia sesión con tus datos.”** Esto **todavía no inicia sesión**.
4. Escribe otra vez la contraseña, porque el formulario la limpia. Pulsa **Entrar**. Debe decir **“Sesión iniciada”**.

### Pestaña B: registrar, iniciar sesión y seguir el municipio

1. Repite los cuatro pasos anteriores en B, **con otro correo**. No uses la misma cuenta.
2. En la barra de secciones de `/comunidad`, pulsa **Alertas**. Baja a **Municipios que sigues**.
3. Escribe `Cuauhtémoc` y pulsa **Seguir municipio**. Verifica que el municipio aparezca en la lista.
4. Haz esto **antes** de publicar el extravío o el hallazgo: la aplicación alerta sobre reportes nuevos, no sobre reportes anteriores a la suscripción.
5. Deja B abierta en esa sección. La bandeja al principio puede estar vacía.

### Pestaña A: guardar la ficha sin publicar

1. En `/comunidad`, pulsa **Mis mascotas**.
2. Llena **Nombre:** `Luna`; **Especie:** `perro`; **Características:** `Pelaje café, collar azul`.
3. Pulsa **Guardar ficha sin publicar**. Debe aparecer Luna en **Mis mascotas**.
4. Detente aquí: **todavía no publiques el extravío**. Esta separación permite mostrar al profesor que la ficha y el reporte son cosas distintas.

Ya puedes empezar la exposición. Amy explica el problema en las diapositivas 1–2; Oscar explica Traefik y las réplicas en la 3; Ceci, identidad en la 4; Luisa, las alertas en la 5. El [guion de voces](GUION_FINAL.md) tiene el texto y los tiempos.

## 5. Demostración en vivo: dónde dar clic

### Paso A. Publicar el extravío desde la ficha de Luna

1. Cambia de la pestaña de diapositivas a **A**. Señala la ficha de Luna en **Mis mascotas**.
2. Dentro de esa ficha, pulsa **Publicar extravío de esta mascota**. La misma pestaña A abre la página principal y baja al formulario. Verás **Ficha de mascota: Luna**; nombre, especie y características ya están llenos.
3. Pulsa **Continuar**. En **El último encuentro**, llena **Última vez vista** con una fecha y hora reciente, **Municipio o alcaldía** con `Cuauhtémoc`, **Colonia** con `Centro` y **Punto de referencia** con `Entrada del parque`.
4. Antes de continuar, mueve el mapa y haz clic en el lugar aproximado del extravío. Debe aparecer un punto rojo y un círculo de 3 km. Pulsa **Continuar**. En **Cómo contactarte**, deja **sin marcar** “Quiero mostrar mi teléfono en el reporte público”. Así podrás demostrar la privacidad.
5. Pulsa **Continuar**, revisa el resumen y pulsa **Publicar y obtener mi enlace**. Debe aparecer **“Tu reporte está publicado”** y un enlace.
6. Di: **“El reporte ya quedó guardado; las alertas se generan después. El enlace se puede compartir.”** Pulsa **Copiar enlace**.

### Paso B. Mostrar el enlace sin iniciar sesión

1. Ve a la pestaña **Público**. Pega el enlace en la barra de direcciones y pulsa Enter.
2. Señala el nombre Luna, las señas, el punto rojo y el círculo de 3 km en el mapa. Si no se ven las calles, comprueba la conexión a Internet; las coordenadas siguen guardadas. Señala que **no aparece un teléfono**, porque A no autorizó mostrarlo.
3. Di: **“Cualquiera que reciba el enlace puede ver el reporte; para publicar o recibir alertas sí hace falta una cuenta.”**

### Paso C. Publicar un hallazgo desde B

1. Cambia a la pestaña **B**. En la barra de secciones pulsa **Hallazgo**.
2. En **Encontré una mascota**, llena **Descripción:** `Perro con collar azul junto al parque`; **Fecha y hora del hallazgo:** fecha y hora reciente; **Municipio o alcaldía:** `Cuauhtémoc`; **Colonia:** `Centro`; **Referencia pública:** `Fuente del parque`.
3. Haz clic en el mapa para marcar el lugar aproximado del hallazgo. Deja desmarcada **“Autorizo mostrar mi teléfono en el reporte público”**. Pulsa **Publicar hallazgo**.
4. Debe aparecer **“Hallazgo publicado”**. Pulsa **Abrir y compartir reporte** si quieres enseñar su enlace. Regresa a B con el botón Atrás del navegador.

### Paso D. Buscar los reportes y ver las alertas

1. En B, pulsa **Reportes** en la barra de secciones. En **Municipio o alcaldía (opcional)** escribe `Cuauhtémoc` y pulsa **Buscar reportes**. Deben aparecer al menos el extravío de Luna y el hallazgo de la demo.
2. Pulsa **Alertas** y baja a **Bandeja de alertas**. Pulsa **Actualizar bandeja**. La alerta puede tardar unos segundos, porque se crea después de guardar el reporte. Si no aparece, espera unos 10 segundos y vuelve a pulsar. La página también consulta automáticamente cada 30 segundos mientras está visible.
3. Abre una alerta para enseñar que lleva a un reporte público. Di: **“La cuenta B seguía este municipio antes de publicar; por eso recibió los avisos. No se enviaron mensajes al teléfono: esta versión usa una bandeja web.”**

### Paso E. Si queda tiempo

En B, pulsa **Cerrar sesión**. Sus municipios y bandeja privados desaparecen de la vista. También puedes mostrar la página con el modo móvil de Chrome (`Ctrl+Shift+M`, ancho 390 px). Estos pasos son opcionales si la exposición va corta.

## 6. Qué hacer si algo no sale como esperabas

| Lo que ves | Qué hacer |
|---|---|
| “Cuenta creada”, pero no aparece “Sesión iniciada” | Vuelve a escribir la contraseña y pulsa **Entrar**. Crear cuenta y entrar son dos acciones distintas. |
| “El correo ya existe” | Pulsa **Entrar** con esa cuenta o usa otro correo ficticio. |
| El mapa no muestra calles | Se necesita Internet para cargar las teselas de OpenStreetMap. El punto rojo y las coordenadas siguen funcionando; no vuelvas a publicar por esto. |
| B no recibe alertas | Comprueba que B pulsó **Seguir municipio** antes del reporte y que el municipio está escrito igual. Espera y pulsa **Actualizar bandeja**. |
| La ficha Luna no aparece al publicar | Vuelve a A, confirma que dice **Sesión iniciada**, entra a **Mis mascotas** y pulsa **Actualizar mis fichas**. Haz clic en **Publicar extravío de esta mascota** desde la ficha. |
| El navegador muestra error de conexión | Comprueba `docker compose ps` en la terminal. Espera unos segundos si los servicios acaban de arrancar. |
| No sabes si una ficha se guardó tras un error | Pulsa **Actualizar mis fichas** antes de repetir el alta, para no crear otra ficha. |
| No sabes si un reporte se publicó tras un error | Reintenta **con el mismo formulario y los mismos datos**. La clave de idempotencia evita duplicar ese intento. |

Si una parte falla durante la exposición, explica qué ocurrió y abre el [PDF de diapositivas](diapositivas.pdf) o los [resultados medidos](../RESULTADOS_FINALES.md). No presentes una captura como si acabara de funcionar en vivo.

## 7. Apagar al terminar

Cuando terminen el ensayo o la exposición, vuelve a la terminal, asegúrate de estar en la carpeta del proyecto y ejecuta:

```bash
docker compose down
```

Esto detiene los contenedores y **conserva** los datos para otro ensayo. Para volver a abrir la app, ejecuta `docker compose up --build -d`. Si quieres comprobar de nuevo el recorrido automático, con la app encendida ejecuta `python3 scripts/smoke_02.py`.
