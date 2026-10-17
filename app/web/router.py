from pathlib import Path
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["web"])
STATIC = Path(__file__).parent / "static"


@router.get("/", response_class=FileResponse)
def home():
    return FileResponse(STATIC / "index.html")


@router.get("/reportes/extravios/{report_id}", response_class=FileResponse)
def public_report(report_id: UUID):
    return FileResponse(STATIC / "report.html")


@router.get("/web/app.js", include_in_schema=False)
def javascript():
    return FileResponse(STATIC / "app.js", media_type="text/javascript")


@router.get("/web/style.css", include_in_schema=False)
def stylesheet():
    return FileResponse(STATIC / "style.css", media_type="text/css")
