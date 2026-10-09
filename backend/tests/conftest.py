"""Pytest fixtures for backend and detection engine tests."""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend and root are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.config import settings
from app.database.session import Base, get_db
from app.main import create_app
from app.models.analyst import AnalystUser
from app.auth.security import hash_password, create_access_token
from app.detection.rule_loader import sync_rules_to_db

TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, future=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all database tables and sync rules once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    # Resolve rules directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    rules_dir = os.path.join(base_dir, "rules")
    sync_rules_to_db(db, rules_dir=rules_dir)

    # Provision standard test users
    admin = AnalystUser(
        username="test_admin",
        password_hash=hash_password("AdminSecret!2026"),
        role="admin",
        is_active=True
    )
    analyst = AnalystUser(
        username="test_analyst",
        password_hash=hash_password("AnalystSecret!2026"),
        role="analyst",
        is_active=True
    )
    viewer = AnalystUser(
        username="test_viewer",
        password_hash=hash_password("ViewerSecret!2026"),
        role="viewer",
        is_active=True
    )
    deactivated = AnalystUser(
        username="test_deactivated",
        password_hash=hash_password("DeactivatedSecret!2026"),
        role="analyst",
        is_active=False
    )
    db.add_all([admin, analyst, viewer, deactivated])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Yield a database session per test with rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def admin_headers():
    token = create_access_token(data={"sub": "test_admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers():
    token = create_access_token(data={"sub": "test_analyst", "role": "analyst"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_headers():
    token = create_access_token(data={"sub": "test_viewer", "role": "viewer"})
    return {"Authorization": f"Bearer {token}"}
