"""Tests for task endpoints."""

from fastapi import status


class TestTasks:
    """Test task endpoints."""

    def test_create_task(self, client, auth_headers):
        """Test creating a new task."""
        response = client.post(
            "/tasks/",
            headers=auth_headers,
            json={
                "title": "New Task",
                "description": "Task description",
                "priority": "high",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["status"] == "pending"

    def test_create_task_unauthorized(self, client):
        """Test creating task without authentication."""
        response = client.post("/tasks/", json={"title": "New Task"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_tasks(self, client, auth_headers, test_task):
        """Test listing tasks."""
        response = client.get("/tasks/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Test Task"

    def test_list_tasks_with_status_filter(self, client, auth_headers, test_task):
        """Test listing tasks with status filter."""
        response = client.get("/tasks/?status=pending", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert all(task["status"] == "pending" for task in data)

    def test_get_task(self, client, auth_headers, test_task):
        """Test getting a specific task."""
        response = client.get(f"/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == "Test Task"

    def test_get_task_not_found(self, client, auth_headers):
        """Test getting a non-existent task."""
        response = client.get("/tasks/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_task(self, client, auth_headers, test_task):
        """Test updating a task."""
        response = client.put(
            f"/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Updated Task", "status": "in_progress"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"

    def test_update_task_unauthorized(
        self, client, auth_headers, test_task, test_user2
    ):
        """Test updating task by non-creator."""
        # Create a task with test_user2
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.put(
            f"/tasks/{test_task.id}",
            headers=user2_headers,
            json={"title": "Unauthorized Update"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_task(self, client, auth_headers, test_task):
        """Test deleting a task."""
        response = client.delete(f"/tasks/{test_task.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_task_unauthorized(
        self, client, auth_headers, test_task, test_user2
    ):
        """Test deleting task by non-creator."""
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.delete(f"/tasks/{test_task.id}", headers=user2_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_task(self, client, auth_headers, test_task, test_user2):
        """Test assigning a task to another user."""
        response = client.post(
            f"/tasks/{test_task.id}/assign",
            headers=auth_headers,
            json={"assigned_user_id": test_user2.id},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["task_id"] == test_task.id
        assert data["assigned_user_id"] == test_user2.id

    def test_assign_task_duplicate(self, client, auth_headers, test_task, test_user2):
        """Test assigning a task to a user who is already assigned."""
        # First assignment
        client.post(
            f"/tasks/{test_task.id}/assign",
            headers=auth_headers,
            json={"assigned_user_id": test_user2.id},
        )
        # Second assignment (should fail)
        response = client.post(
            f"/tasks/{test_task.id}/assign",
            headers=auth_headers,
            json={"assigned_user_id": test_user2.id},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_assign_task_unauthorized(
        self, client, auth_headers, test_task, test_user2
    ):
        """Test assigning task by non-creator."""
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.post(
            f"/tasks/{test_task.id}/assign",
            headers=user2_headers,
            json={"assigned_user_id": test_user2.id},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_assignments(self, client, auth_headers, test_task, test_user2):
        """Test listing assignments for a task."""
        # First assign the task
        client.post(
            f"/tasks/{test_task.id}/assign",
            headers=auth_headers,
            json={"assigned_user_id": test_user2.id},
        )

        response = client.get(
            f"/tasks/{test_task.id}/assignments", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["task_id"] == test_task.id

    def test_complete_task(self, client, auth_headers, test_task):
        """Test completing a task."""
        response = client.post(f"/tasks/{test_task.id}/complete", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_complete_task_already_completed(self, client, auth_headers, test_task):
        """Test completing an already completed task."""
        # First complete the task
        client.post(f"/tasks/{test_task.id}/complete", headers=auth_headers)
        # Try to complete again
        response = client.post(f"/tasks/{test_task.id}/complete", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_complete_task_unauthorized(
        self, client, auth_headers, test_task, test_user2
    ):
        """Test completing task by unauthorized user."""
        from app.core.security import create_access_token

        user2_headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user2.email})}"  # noqa: E501
        }

        response = client.post(f"/tasks/{test_task.id}/complete", headers=user2_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
