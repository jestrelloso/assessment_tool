from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from app.main import app
from utils.config import settings
from db.database import get_db, Base
from sqlalchemy.orm import sessionmaker
from auth.oauth2 import create_access_token
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
def test_examinee(client):
    examinee_data = {
        "email_auth": False,
        "email": "examinee@example.com",
        "first_name": "Examinee",
        "last_name": "Examinee",
        "password": "password123",
        "phone_number": "1234567890",
        "four_digit_code": None,
    }
    image_file = BytesIO(b"fake image data")
    files = {
        "user": (None, json.dumps(examinee_data), "application/json"),
        "image": ("dummy.jpg", image_file, "image/jpeg"),
    }
    res = client.post("/users", files=files)
    assert res.status_code == 201
    new_examinee = res.json()
    new_examinee["password"] = examinee_data["password"]
    return new_examinee


@pytest.fixture()
def test_admin(client):
    admin_data = {
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "Admin",
        "password": "password123",
    }
    image_file = BytesIO(b"fake image data")
    files = {
        "admin": (None, json.dumps(admin_data), "application/json"),
        "image": ("dummy.jpg", image_file, "image/jpeg"),
    }
    res = client.post("/admin", files=files)
    assert res.status_code == 201
    new_admin = res.json()
    return new_admin


@pytest.fixture()
def test_examiner(client):
    examiner_data = {
        "email": "examiner@example.com",
        "first_name": "Examiner",
        "last_name": "Examiner",
        "password": "password123",
    }
    image_file = BytesIO(b"fake image data")
    files = {
        "examiner": (None, json.dumps(examiner_data), "application/json"),
        "image": ("dummy.jpg", image_file, "image/jpeg"),
    }
    res = client.post("/examiner", files=files)
    assert res.status_code == 201
    new_examinee = res.json()
    return new_examinee


@pytest.fixture()
def token(test_examinee, test_admin):
    examinee_token = create_access_token({"user_id": test_examinee["id"]})
    admin_token = create_access_token({"user_id": test_admin["id"]})
    return {
        "examinee": examinee_token,
        "admin": admin_token,
    }


@pytest.fixture()
def token_examiner(test_examiner):
    return create_access_token(
        {"user_id": test_examiner["id"], "user_type": test_examiner["user_type"]}
    )


@pytest.fixture()
def authorized_examiner(client, token_examiner):
    client.headers = {**client.headers, "Authorization": f"Bearer {token_examiner}"}
    return client


@pytest.fixture()
def token_examinee(test_examinee):
    return create_access_token(
        {"user_id": test_examinee["id"], "user_type": test_examinee["user_type"]}
    )


@pytest.fixture()
def authorized_examinee(client, token_examinee):
    client.headers = {**client.headers, "Authorization": f"Bearer {token_examinee}"}
    return client


@pytest.fixture()
def test_exam(client, token_examiner):
    exam_data = {
        "title": "Dummy Exam",
        "total_questions": 4,
        "time_duration": 60,
        "description": "This is a dummy exam for testing purposes.",
        "passing_rate": 70,
        "enrollees": 100,
        "exam_topic": "General Knowledge",
        "grading_system": "Percentage",
        "number_of_items": 2,
        "topics": [
            {
                "name": "Mathematics",
                "questions": [
                    {
                        "question": "What is 3 multiplied by 5?",
                        "correct_answer": "15",
                        "answer_temp": "",
                        "options_temp": "None",
                        "choices": [
                            {"option": "10"},
                            {"option": "12"},
                            {"option": "15"},
                            {"option": "18"},
                        ],
                    },
                    {
                        "question": "What is the result of 20 divided by 4?",
                        "correct_answer": "5",
                        "answer_temp": "",
                        "options_temp": "None",
                        "choices": [
                            {"option": "3"},
                            {"option": "4"},
                            {"option": "5"},
                            {"option": "6"},
                        ],
                    },
                ],
            },
            {
                "name": "Science",
                "questions": [
                    {
                        "question": "What is the chemical symbol for oxygen?",
                        "correct_answer": "O",
                        "answer_temp": "",
                        "options_temp": "None",
                        "choices": [
                            {"option": "O"},
                            {"option": "H2O"},
                            {"option": "CO2"},
                            {"option": "NaCl"},
                        ],
                    },
                    {
                        "question": "What is the atomic number of carbon?",
                        "correct_answer": "6",
                        "answer_temp": "",
                        "options_temp": "None",
                        "choices": [
                            {"option": "4"},
                            {"option": "6"},
                            {"option": "8"},
                            {"option": "10"},
                        ],
                    },
                ],
            },
        ],
    }

    image_file = BytesIO(b"fake image data")
    files = {
        "exam": (None, json.dumps(exam_data), "application/json"),
        "image": ("dummy.jpg", image_file, "image/jpeg"),
    }
    headers = {"Authorization": f"Bearer {token_examiner}"}
    res = client.post("/exams", files=files, headers=headers)
    assert res.status_code == 200
    new_exam = res.json()
    return new_exam


@pytest.fixture
def test_request_exam(client, token_examinee, test_exam):
    request_exam = test_exam["id"]
    headers = {"Authorization": f"Bearer {token_examinee}"}
    res = client.post(f"/request_exam/?request_exam={request_exam}", headers=headers)

    assert res.status_code == 201
    new_request_exam = res.json()

    return new_request_exam


@pytest.fixture
def mock_exam():
    return {
        "title": "Dummy Exam",
        "total_questions": 4,
        "time_duration": 60,
        "description": "This is a dummy exam for testing purposes.",
        "passing_rate": 70,
        "enrollees": 100,
        "exam_topic": "General Knowledge",
        "grading_system": "Percentage",
        "number_of_items": 2,
        "topics": [
            {
                "name": "Mathematics",
                "questions": [
                    {
                        "question": "What is 3 multiplied by 5?",
                        "correct_answer": "15",
                        "answer_temp": "",
                        "options_temp": "None",
                        "choices": [
                            {"option": "10"},
                            {"option": "12"},
                            {"option": "15"},
                            {"option": "18"},
                        ],
                    }
                ],
            }
        ],
    }
