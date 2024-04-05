import uuid
import json


# GET test
def test_get_user(client, test_user):
    # Test retrieving a user
    response = client.get(f"/users/{test_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["first_name"] == test_user["first_name"]
    assert data["last_name"] == test_user["last_name"]
    assert "password" not in data


# GET all users test
def test_get_all_users(client):
    # Test retrieving all users
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # The response should be a list of users


# GET user not found test
def test_user_not_found(client):
    # Test retrieving a user that does not exist
    non_existent_id = uuid.uuid4()  # Generate a random UUID
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404  # The server should return a 404 status code


# POST test
def test_create_user(client):
    # Test creating a new user
    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test1@example.com", "exams": ["exam1", "exam2"], "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "profile_image": null, "four_digit_code": null}'
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
    # Test creating a user with an email that's already in use
    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test2@example.com", "exams": ["exam1", "exam2"], "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "profile_image": null, "four_digit_code": null}'
            },
            files={"image": ("frieren.jpg", img_file, "image/jpeg")},
        )
    assert response.status_code == 201

    # Now try creating another user with the same email
    with open("images/frieren.jpg", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test2@example.com", "exams": ["exam1", "exam2"], "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "profile_image": null, "four_digit_code": null}'
            },
            files={"image": ("frieren.jpg", img_file, "image/jpeg")},
        )
    assert response.status_code == 400


def test_create_user_with_invalid_image_type(client):
    # Test creating a new user with an unsupported image type
    with open("images/unsupported_file_type.txt", "rb") as img_file:
        response = client.post(
            "/users",
            data={
                "user": '{"email_auth": false, "email": "test1@example.com", "exams": ["exam1", "exam2"], "first_name": "John", "last_name": "Doe", "password": "password123", "phone_number": "1234567890", "profile_image": null, "four_digit_code": null}'
            },
            files={"image": ("unsupported_file_type.txt", img_file, "text/plain")},
        )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid file type. Only .jpg and .png files are accepted"


# PUT test
def test_update_user(client, test_user):
    # Test updating a user
    update_data = {
        "first_name": "Update Name",
        "last_name": "Update Surname",
    }
    files = {
        "post_user": (None, json.dumps(update_data), "application/json"),
    }
    response = client.put(
        f"/users/{str(test_user['id'])}",
        files=files,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]


def test_update_user_image_only(client, test_user):
    # Test updating a user's image
    with open("images/gon.jpg", "rb") as image_file:
        files = {
            "profile_image": image_file,
        }
        response = client.put(
            f"/users/{str(test_user['id'])}",
            files=files,
        )
    assert response.status_code == 200


def test_update_user_unsupported_file_type(client, test_user):
    # Test updating a user's image with an unsupported file type
    with open("images/unsupported_file_type.txt", "rb") as image_file:
        files = {
            "profile_image": image_file,
        }
        response = client.put(
            f"/users/{str(test_user['id'])}",
            files=files,
        )
    assert response.status_code == 400


def test_update_user_and_image(client, test_user):
    # Test updating a user's data and image
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
            f"/users/{str(test_user['id'])}",
            files=files,
        )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == "newemail@example.com"
    # Check that the profile_image field has been updated
    assert updated_user["profile_image"] is not None


# Delete Test
def test_delete_user(client, test_user):
    response = client.delete(
        f"/users/{str(test_user['id'])}",
    )
    assert response.status_code == 204


def test_delete_user_non_exist(client):
    non_existent_uuid = uuid.uuid4()
    res = client.delete(f"/users/{non_existent_uuid}")
    assert res.status_code == 404
