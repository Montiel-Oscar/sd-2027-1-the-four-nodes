# Servicio de identidad

`app/identity/main.py` expone internamente el puerto 8002. Traefik enruta `/api/usuarios` desde `http://localhost:8000` a este proceso. Su base lógica es `four_nodes_identity`; las contraseñas se guardan como hashes Argon2id. El contrato público conserva registro, login y `/me` de la etapa anterior.

`app/identity/migrate.py` crea la tabla propia y copia de forma idempotente cuentas históricas de `four_nodes.users` si existen. No borra el volumen ni cambia los UUID, hashes o tokens vigentes. La tabla histórica permanece para preservar datos previos, pero reportes ya no la crea ni consulta. En una instalación nueva, identidad crea su tabla exclusivamente en la base propia.

`AUTH_SECRET` se comparte con reportes y alertas. Los JWT HS256 contienen `sub`, emisor y vencimiento de 60 minutos. Reportes y alertas validan firma y vencimiento localmente. Si identidad se detiene, registro y login dejan de funcionar; un token válido puede seguir autorizando publicación. Cambiar `AUTH_SECRET` invalida los tokens anteriores.

Para probar: iniciar Compose desde la raíz, registrar dos cuentas en `/comunidad`, confirmar que cada una sólo ve sus mascotas, ejecutar `python3 scripts/smoke_02.py` y consultar `docs/RESULTADOS_FINALES.md`. Las pruebas de unidad de JWT, correo duplicado, token vencido, privacidad y contraseñas están en `tests/test_identity.py`.
