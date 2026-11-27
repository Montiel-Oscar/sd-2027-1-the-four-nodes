# Material del pitch final

- [Diapositivas PDF](diapositivas.pdf) y [HTML navegable](diapositivas.html): siete pantallas, sin conexión a Internet. En HTML usar flechas, Inicio o los botones visibles.
- [Guion final de los cuatro integrantes y demostración clic por clic](GUION_FINAL.md): preparación, tiempos, reparto, acciones y preguntas de defensa.
- [Guía para abrir la app y manejar las pestañas](GUIA_DEMO_PASO_A_PASO.md): comandos, cuentas ficticias, campos, clics y solución de problemas.
- [Resultados](../RESULTADOS_FINALES.md) y [reporte final](../reporte-final.pdf): evidencia de las afirmaciones técnicas.

El profesor no fijó una duración en la rúbrica. El guion propone cinco minutos; practicarlo con cámara y ajustar al tiempo que indique el profesor. Todos presentan y deben poder defender la arquitectura. `capturas/` es material de respaldo local; una imagen de prueba no sustituye una demostración en vivo.

Para regenerar el PDF desde HTML, instalar Playwright y ejecutar `python3 docs/pitch/export_slides.py`. Para verificar el recorrido de dos cuentas sobre los servicios reales: `python3 app/web/tests/verify_final_demo.py --base-url http://localhost:8000 --output /tmp/four-nodes-demo`.
