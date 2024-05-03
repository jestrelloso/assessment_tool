from schemas import schemas
from jose import jwt
from utils.config import settings
import pytest
import uuid
import json


# GET test
def test_get_user(client, test_examinee):
    response = client.get(f"/users/{test_examinee['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_examinee["email"]
    assert data["first_name"] == test_examinee["first_name"]
    assert data["last_name"] == test_examinee["last_name"]
    assert "password" not in data


# GET all users test
def test_get_all_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# GET user not found test
def test_user_not_found(client):

    non_existent_id = uuid.uuid4()
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404


# POST test
def test_create_user(client):
    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test1@example.com", "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "four_digit_code": null}'
            },
            files={"image": ("frieren.jpg", img_file, "image/jpeg")},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test1@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "password" not in data


def test_create_user_with_existing_email(client):
    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test2@example.com", "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "four_digit_code": null}'
            },
            files={"image": ("frieren.jpg", img_file, "image/jpeg")},
        )
    assert response.status_code == 201

    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test2@example.com", "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "four_digit_code": null}'
            },
            files={"image": ("frieren.jpg", img_file, "image/jpeg")},
        )
    assert response.status_code == 400


def test_create_user_with_invalid_image_type(client):
    with open("images/unsupported_file_type.txt", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test1@example.com", "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "four_digit_code": null}'
            },
            files={"image": ("unsupported_file_type.txt", img_file, "text/plain")},
        )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid file type. Only .jpg and .png files are accepted"


# PUT test
def test_update_user(client, test_examinee):
    update_data = {
        "first_name": "Update Name",
        "last_name": "Update Surname",
    }
    files = {
        "post_user": (None, json.dumps(update_data), "application/json"),
    }
    response = client.put(
        f"/users/{str(test_examinee['id'])}",
        files=files,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]


def test_update_user_image_only(client, test_examinee):
    with open("images/gon.jpg", "rb") as image_file:
        files = {
            "profile_image": image_file,
        }
        response = client.put(
            f"/users/{str(test_examinee['id'])}",
            files=files,
        )
    assert response.status_code == 200


def test_update_user_unsupported_file_type(client, test_examinee):
    with open("images/unsupported_file_type.txt", "rb") as image_file:
        files = {
            "profile_image": image_file,
        }
        response = client.put(
            f"/users/{str(test_examinee['id'])}",
            files=files,
        )
    assert response.status_code == 400


def test_update_user_and_image(client, test_examinee):
    updated_user_data = {
        "email": "newemail@example.com",
        "password": "newpassword",
    }
    with open("images/gon.jpg", "rb") as image_file:
        files = {
            "post_user": (None, json.dumps(updated_user_data), "application/json"),
            "profile_image": image_file,
        }
        response = client.put(
            f"/users/{str(test_examinee['id'])}",
            files=files,
        )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == "newemail@example.com"
    assert updated_user["profile_image"] is not None


# Delete Test
def test_delete_user(client, test_examinee):
    response = client.delete(
        f"/users/{str(test_examinee['id'])}",
    )
    assert response.status_code == 204


def test_delete_user_non_exist(client):
    non_existent_uuid = uuid.uuid4()
    res = client.delete(f"/users/{non_existent_uuid}")
    assert res.status_code == 404


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Login test


def test_login_user(test_examinee, client):
    res = client.post(
        "/login",
        data={
            "username": test_examinee["email"],
            "password": test_examinee["password"],
        },
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id = payload.get("user_id")
    assert id == test_examinee["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("jeremiad1@example.com", "password123", 403),
        ("jeremiah1213@example.com", "wrongPassword", 403),
        ("jeremiah21@example.com", "wrongPassword", 403),
        (None, "password123", 422),
        ("jeremiah1231", None, 422),
    ],
)
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
