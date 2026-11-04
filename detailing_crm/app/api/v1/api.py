from fastapi import APIRouter

from app.api.v1.endpoints import bookings, webhooks

api_router = APIRouter()
api_router.include_router(webhooks.router)
api_router.include_router(bookings.router)
