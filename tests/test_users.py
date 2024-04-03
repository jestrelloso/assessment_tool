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
