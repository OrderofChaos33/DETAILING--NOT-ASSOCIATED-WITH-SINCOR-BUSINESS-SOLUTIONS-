"""Clinton Auto Detailing — frictionless booking engine (production config).

Security posture from the owner's 2026-11-04 paste, kept intact:
- Trusted hosts: clintondetail.com / www only (+ localhost for dev)
- CORS: clintondetail.com origins only — the earlier allow_origins=["*"]
  draft is superseded and deliberately NOT used here
- Public API docs disabled in production; security headers on every response
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.api.v1.api import api_router
from app.core.config import SHOP_ADDRESS, SHOP_NAME

app = FastAPI(
    title="Clinton Auto Detailing Engine",
    description="Frictionless booking backend for clintondetail.com",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["clintondetail.com", "www.clintondetail.com", "localhost", "127.0.0.1"],
)

origins = [
    "https://clintondetail.com",
    "https://www.clintondetail.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = "default-src 'self' https://clintondetail.com;"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "online", "shop": SHOP_NAME, "location": SHOP_ADDRESS}


# --- Customer-facing site (frontend/) -------------------------------------
# Served same-origin so the strict CSP above ('self') covers its CSS/JS —
# the page uses external styles.css / app.js, no inline scripts or styles.
# Mounted LAST so /api/v1 routes and /health always win. FRONTEND_DIR can
# override the location (the Docker image sets it); if the folder is absent
# (API-only deployment), the API runs unchanged.
import os
from pathlib import Path

from fastapi.staticfiles import StaticFiles

_FRONTEND_DIR = Path(
    os.environ.get("FRONTEND_DIR", Path(__file__).resolve().parents[2] / "frontend")
)
if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
