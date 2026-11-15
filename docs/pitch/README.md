# Pitch y evidencia de interfaz

- [Diapositivas HTML](diapositivas.html): siete pantallas, sin Internet; flechas e Inicio, botones y versión móvil.
- [Diapositivas PDF](diapositivas.pdf): respaldo imprimible, exportado del HTML.
- [Guion de demo](GUION_DEMO.md): preparación, dos cuentas, orden, reparto de voces, variante base de cinco minutos y respaldo.
- [Aporte al reporte](APORTE_REPORTE_AMY.md): problema, público, recorrido, diagrama funcional, decisiones de interfaz y límites para que Oscar los incorpore al PDF final.
- `capturas/`: imágenes originales de navegador con datos ficticios; leer `entorno.json` antes de usarlas como evidencia.

La rúbrica no fija duración del pitch: confirmar con el profesor y ajustar el ensayo. Todos presentan una parte. Este PDF de slides **no es** `docs/reporte-final.pdf`, asignado a Oscar tras la integración.

## Reproducir

Desde la raíz, instalar las dependencias del proyecto y Playwright en el entorno de pruebas. Microsoft Edge debe estar instalado; también se puede definir `PLAYWRIGHT_BROWSER` con la ruta de Chrome/Chromium.

```powershell
python -m pip install -e '.[dev]' playwright
python app/web/tests/verify_browser.py
python app/web/tests/verify_final_demo.py
python docs/pitch/export_slides.py
```

`verify_browser.py` simula las respuestas para provocar fallos de red, 401 y 409; verifica reintentos y campos. `verify_final_demo.py` usa las rutas reales de identidad, mascotas, reportes y alertas con bases SQLite temporales y transporte TestClient, sin lanzar Docker. Procesa explícitamente los eventos con la lógica real de alertas y los reentrega para probar deduplicación; no simula latencia ni certifica el trabajador temporizado, Traefik o PostgreSQL.

Para el recorrido sobre los servicios reales levantados según el README:

```powershell
python app/web/tests/verify_final_demo.py --base-url http://localhost:8000 --output docs/pitch/capturas-en-vivo
```

Ese comando crea cuentas y reportes ficticios con sufijos únicos, y espera la bandeja real hasta tres minutos. No borra datos. Si falla, no se genera un resultado exitoso. Revisar las capturas antes de incorporarlas al reporte. Si se conserva otro directorio de capturas, incluir también su `entorno.json`.

Pendiente de ensayo del equipo: confirmar duración, sustituir cualquier nota de integración por el estado probado y añadir los tiempos medidos de Luisa. No afirmar que las capturas locales demuestran continuidad ante caída de réplicas.
