def test_admin_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ecommerce-intel.io", "password": "Admin123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@ecommerce-intel.io"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ecommerce-intel.io", "password": "WrongPassword!"},
    )
    assert response.status_code == 401


def test_user_registration(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@ecommerce-intel.io",
            "password": "SecurePassword123!",
            "full_name": "Data Analyst",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "analyst@ecommerce-intel.io"
    assert data["full_name"] == "Data Analyst"
