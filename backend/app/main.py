"""SentinelEDR Main FastAPI Application."""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings
from app.database.session import engine, Base, SessionLocal
from app.models.analyst import AnalystUser
from app.auth.security import hash_password
from app.detection.rule_loader import sync_rules_to_db
from app.api.v1 import api_router

# Configure structured logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sentinel.app")


def bootstrap_database_and_admin():
    """Create tables, ensure admin user exists, and sync YAML detection rules."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if any admin exists
        existing_admin = db.query(AnalystUser).filter(AnalystUser.username == settings.bootstrap_admin_username).first()
        if not existing_admin:
            logger.info(f"Bootstrapping default administrator '{settings.bootstrap_admin_username}'...")
            admin = AnalystUser(
                username=settings.bootstrap_admin_username,
                password_hash=hash_password(settings.bootstrap_admin_password),
                role=settings.bootstrap_admin_role,
                is_active=True
            )
            db.add(admin)
            db.commit()
            logger.info("Administrator successfully bootstrapped.")

        # Sync detection rules
        synced = sync_rules_to_db(db, rules_dir=settings.rules_dir)
        logger.info(f"Synchronized {synced} detection rules to database.")
    except Exception as e:
        logger.error(f"Error during bootstrap: {e}", exc_info=True)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup and shutdown procedures."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]...")
    bootstrap_database_and_admin()
    yield
    logger.info(f"Shutting down {settings.app_name}...")


def create_app() -> FastAPI:
    """Application factory for SentinelEDR Backend API."""
    app = FastAPI(
        title=settings.app_name,
        description="Local-first Endpoint Detection and Response (EDR) API platform.",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )

    # Configure CORS
    allowed_origins = settings.cors_origins
    if isinstance(allowed_origins, str):
        allowed_origins = [o.strip() for o in allowed_origins.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request performance & logging middleware
    @app.middleware("http")
    async def add_process_time_and_log(request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
            return response
        except Exception as exc:
            logger.error(f"Unhandled server error on {request.method} {request.url.path}: {exc}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "An internal server error occurred. Check system logs."}
            )

    # Health check endpoint
    @app.get("/health", tags=["System"])
    def health_check():
        db_status = "connected"
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            db_status = f"unhealthy: {e}"

        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "app": settings.app_name,
            "version": settings.app_version,
            "database": db_status,
            "demo_mode": settings.demo_mode
        }

    @app.get("/", tags=["System"])
    def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "SentinelEDR API Server. Access /docs for OpenAPI specification.",
            "health": "/health"
        }

    # Mount API v1 router
    app.include_router(api_router)

    return app


app = create_app()
