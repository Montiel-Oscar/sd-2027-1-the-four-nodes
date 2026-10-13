# Cómo colaborar en `01-monolito`

## Antes de comenzar

Oscar comparte el enlace del repositorio y, en **Settings → Collaborators**, invita a [@LuisaCedeno](https://github.com/LuisaCedeno), [@CeciliaXimenaSolisCisneros](https://github.com/CeciliaXimenaSolisCisneros), [@Amyv19](https://github.com/Amyv19) y al profesor [@OscarRuiz21](https://github.com/OscarRuiz21), como exige el README del curso. Cada integrante acepta su invitación, configura su **propio** nombre y correo de Git, lee [el PRD](PRD.md) y revisa [el reparto](REPARTO_01_MONOLITO.md). Los commits de cada persona deben quedar con su identidad: el profesor revisará el historial.

## Con GitHub Desktop

1. Clonar `Montiel-Oscar/sd-2027-1-the-four-nodes` desde **File → Clone repository**. Oscar, si ya tiene la carpeta local, puede usar **File → Add local repository**.
2. En **Current branch**, seleccionar `01-monolito` y hacer **Fetch origin / Pull origin**.
3. Crear una rama personal desde `01-monolito`: `trabajo/oscar-extravios`, `trabajo/luisa-mascotas`, `trabajo/cecilia-identidad` o `trabajo/amy-web`.
4. Trabajar en la carpeta asignada. Revisar los archivos cambiados antes de **Commit to ...** y después usar **Publish branch / Push origin**.
5. Abrir una propuesta de integración hacia **`01-monolito`**. Otro integrante revisa, se corrigen los comentarios y se integra. Después, todos hacen **Fetch/Pull** de `01-monolito`.

## Con Git en terminal

```bash
git clone https://github.com/Montiel-Oscar/sd-2027-1-the-four-nodes.git
cd sd-2027-1-the-four-nodes
git switch 01-monolito
git pull origin 01-monolito
git switch -c trabajo/TU-NOMBRE-TAREA
# editar solamente tus archivos asignados
git add app/TU-CARPETA
git commit -m "feat: implementar TU-TAREA"
git push -u origin trabajo/TU-NOMBRE-TAREA
```

El `git add` anterior es un ejemplo: incluye también pruebas o documentación que hayas creado. Abre la propuesta de integración en GitHub con base `01-monolito`.

## Reglas para evitar conflictos

- El esqueleto común y los contratos están listos antes de repartir trabajo. Cada integrante modifica principalmente su carpeta. Si necesita cambiar `app/core/`, `app/main.py` o `compose.yaml`, lo anuncia primero al equipo.
- No suban `.env`, contraseñas, tokens, bases de datos ni archivos `__pycache__`.
- Antes de integrar, levanten `docker compose up --build` y comprueben que `/health/ready` responde. Un endpoint nuevo debe tener al menos una prueba que compruebe su comportamiento principal o de falla.
- Una sola persona integra por vez en `01-monolito`. Después de cada integración, los demás actualizan su rama desde `01-monolito` y resuelven conflictos localmente.
- La primera entrega es el monolito: no separen servicios ni agreguen Traefik todavía.
