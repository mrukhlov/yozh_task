"""Pytest configuration and fixtures."""

import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.comment import Comment
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

load_dotenv()

DB_PORT = os.environ.get("DB_PORT", "5460")

# Test database - using the same container as main app but different database
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:password@localhost:{DB_PORT}/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_test_database():
    """Create test database if it doesn't exist."""
    # Connect to default postgres database to create test database
    default_engine = create_engine(
        f"postgresql://postgres:password@localhost:{DB_PORT}/postgres"
    )
    try:
        with default_engine.connect() as conn:
            conn.execute(text("COMMIT"))  # Close any open transaction
            conn.execute(text("CREATE DATABASE test_db"))
    except Exception:
        # Database might already exist, which is fine
        pass
    finally:
        default_engine.dispose()


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create test database and tables."""
    create_test_database()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Database session fixture."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db):
    """Create a second test user."""
    from app.core.security import get_password_hash

    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    from app.core.security import get_password_hash

    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_headers(admin_user):
    """Get authentication headers for admin user."""
    access_token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_task(db, test_user):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test task description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        creator_id=test_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def test_comment(db, test_user, test_task):
    """Create a test comment."""
    comment = Comment(
        content="Test comment", task_id=test_task.id, author_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
