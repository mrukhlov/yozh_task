"""Tests for user endpoints."""

from fastapi import status


class TestUsers:
    """Test user endpoints."""

    def test_get_me(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    def test_get_me_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_admin(self, client, admin_headers, test_user, test_user2):
        """Test listing users as admin."""
        response = client.get("/users/", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3  # admin + test_user + test_user2
        emails = [user["email"] for user in data]
        assert "admin@example.com" in emails
        assert "test@example.com" in emails
        assert "test2@example.com" in emails

    def test_list_users_non_admin(self, client, auth_headers):
        """Test listing users as non-admin user."""
        response = client.get("/users/", headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_me(self, client, auth_headers):
        """Test updating current user profile."""
        response = client.put(
            "/users/me",
            headers=auth_headers,
            json={"username": "updateduser", "email": "updated@example.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "updateduser"
        assert data["email"] == "updated@example.com"

    def test_update_me_password(self, client, auth_headers):
        """Test updating current user password."""
        response = client.put(
            "/users/me", headers=auth_headers, json={"password": "newpassword123"}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_update_me_unauthorized(self, client):
        """Test updating user profile without authentication."""
        response = client.put("/users/me", json={"username": "updateduser"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_me(self, client, auth_headers):
        """Test deleting current user account."""
        response = client.delete("/users/me", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_me_unauthorized(self, client):
        """Test deleting user account without authentication."""
        response = client.delete("/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
