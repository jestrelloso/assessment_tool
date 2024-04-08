from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from app.main import app
from utils.config import settings
from db.database import get_db, Base
from sqlalchemy.orm import sessionmaker
import json
from io import BytesIO

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {
        "email_auth": False,
        "email": "example@example.com",
        "exams": ["exam1", "exam2"],
        "first_name": "Gon",
        "last_name": "Freeccs",
        "password": "password123",
        "phone_number": "1234567890",
        "four_digit_code": None,
    }
    image_file = BytesIO(b"fake image data")
    files = {
        "user": (None, json.dumps(user_data), "application/json"),
        "image": ("dummy.jpg", image_file, "image/jpeg"),
    }
    res = client.post("/users", files=files)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user
