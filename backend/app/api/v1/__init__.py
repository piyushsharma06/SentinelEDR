"""API v1 Router aggregation."""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.hosts import router as hosts_router
from app.api.v1.events import router as events_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.rules import router as rules_router
from app.api.v1.audit import router as audit_router
from app.api.v1.stats import router as stats_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(hosts_router)
api_router.include_router(events_router)
api_router.include_router(alerts_router)
api_router.include_router(incidents_router)
api_router.include_router(rules_router)
api_router.include_router(audit_router)
api_router.include_router(stats_router)

__all__ = ["api_router"]
