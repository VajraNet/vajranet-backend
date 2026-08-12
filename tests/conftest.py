import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.session import get_db
from app.db import session as db_session_module
from app.models.base import Base
from app.main import app

# Use a test SQLite database
TEST_DATABASE_URL = "sqlite:///./test_vajranet.db"
settings.DATABASE_URL = TEST_DATABASE_URL

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

db_session_module.engine = test_engine
db_session_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before test session and drop after."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_vajranet.db"):
        try:
            os.remove("./test_vajranet.db")
        except Exception:
            pass


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh transactional database session per test function."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def citizen_auth():
    return {"Authorization": "Bearer mock-citizen-token"}


@pytest.fixture
def volunteer_auth():
    return {"Authorization": "Bearer mock-volunteer-token"}


@pytest.fixture
def government_auth():
    return {"Authorization": "Bearer mock-government-token"}


@pytest.fixture
def admin_auth():
    return {"Authorization": "Bearer mock-admin-token"}
