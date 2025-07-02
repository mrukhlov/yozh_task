"""Tests for comment endpoints."""

from fastapi import status


class TestComments:
    """Test comment endpoints."""

    def test_get_comments_for_task(self, client, auth_headers, test_task, test_comment):
        """Test getting comments for a task."""
        response = client.get(f"/comments/task/{test_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["content"] == "Test comment"
        assert data[0]["task_id"] == test_task.id

    def test_get_comments_for_nonexistent_task(self, client, auth_headers):
        """Test getting comments for a non-existent task."""
        response = client.get("/comments/task/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_comment(self, client, auth_headers, test_task):
        """Test adding a comment to a task."""
        response = client.post(
            f"/comments/task/{test_task.id}",
            headers=auth_headers,
            json={"content": "New comment"},
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == "New comment"
        assert data["task_id"] == test_task.id

    def test_add_comment_to_nonexistent_task(self, client, auth_headers):
        """Test adding a comment to a non-existent task."""
        response = client.post(
            "/comments/task/999", headers=auth_headers, json={"content": "New comment"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_comment_unauthorized(self, client, test_task):
        """Test adding a comment without authentication."""
        response = client.post(
            f"/comments/task/{test_task.id}", json={"content": "New comment"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_comment(self, client, auth_headers, test_comment):
        """Test updating a comment."""
        response = client.put(
            f"/comments/{test_comment.id}",
            headers=auth_headers,
            json={"content": "Updated comment"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Updated comment"

    def test_update_comment_unauthorized(
        self, client, auth_headers, test_comment, test_user2
    ):
        """Test updating a comment by non-author."""
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.put(
            f"/comments/{test_comment.id}",
            headers=user2_headers,
            json={"content": "Unauthorized update"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_nonexistent_comment(self, client, auth_headers):
        """Test updating a non-existent comment."""
        response = client.put(
            "/comments/999", headers=auth_headers, json={"content": "Updated comment"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_comment(self, client, auth_headers, test_comment):
        """Test deleting a comment."""
        response = client.delete(f"/comments/{test_comment.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_comment_unauthorized(
        self, client, auth_headers, test_comment, test_user2
    ):
        """Test deleting a comment by non-author."""
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.delete(f"/comments/{test_comment.id}", headers=user2_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_nonexistent_comment(self, client, auth_headers):
        """Test deleting a non-existent comment."""
        response = client.delete("/comments/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
