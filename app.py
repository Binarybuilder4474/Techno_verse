"""
Main entry point. Run the whole system with:

    uvicorn app:app --reload

Routers (one file per feature) are registered in the ROUTERS list below.
They will be added batch by batch.
"""
import importlib
import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import STATIC_DIR
from database import check_connection

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("exam")

app = FastAPI(title="Secure Examination Management System")

# Module names inside the routers/ package. Add new ones here as they are built.
ROUTERS: list[str] = [
    # "auth", "users", "exams", "questions", "enrollments", "attempts",
    # "monitoring", "grading", "results", "reports", "imports", "analytics",
    # "integrity", "fairness", "disputes",
]

for name in ROUTERS:
    module = importlib.import_module(f"routers.{name}")
    app.include_router(module.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "database": "connected" if check_connection() else "unreachable"}


# ---- Frontend (monolithic: served by FastAPI itself) ----
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
