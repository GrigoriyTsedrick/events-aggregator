"""Главный роутер v1."""

from fastapi import APIRouter

from src.api.v1.endpoints import events, health, sync, tickets

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(sync.router)
api_router.include_router(events.router)
api_router.include_router(tickets.router)
