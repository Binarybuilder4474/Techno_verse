"""
Main entry point. Run the whole system with:

    uvicorn app:app --reload

Routers (one file per feature) are registered in the ROUTERS list below.
"""
import importlib
import logging

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import STATIC_DIR
from database import check_connection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("exam")

app = FastAPI(title="Secure Examination Management System")

# Module names inside the routers/ package. Add new ones here as they are built.
ROUTERS: list[str] = [
    "auth", "users", "questions", "exams", "enrollments",
    # coming next: "attempts", "monitoring", "grading", "results", "reports",
    # "imports", "analytics", "integrity", "fairness", "disputes",
]

for name in ROUTERS:
    module = importlib.import_module(f"routers.{name}")
    app.include_router(module.router)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)
    return JSONResponse({"detail": "Something went wrong on the server. Please try again."}, status_code=500)


@app.get("/api/health")
def health():
    return {"status": "ok", "database": "connected" if check_connection() else "unreachable"}


# ---- Frontend (monolithic: served by FastAPI itself) ----
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})
