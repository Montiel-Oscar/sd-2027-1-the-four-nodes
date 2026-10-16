from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["web"])


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Four Nodes</title>
<style>body{font-family:system-ui,sans-serif;max-width:44rem;margin:4rem auto;padding:0 1rem;line-height:1.5}a{color:#155e75}</style>
</head>
<body><h1>The Four Nodes</h1><p>Búsqueda comunitaria de mascotas.</p>
<p>El equipo está construyendo el primer flujo: publicar un extravío.</p>
<p><a href="/docs">Ver la documentación de la API</a></p></body></html>"""
