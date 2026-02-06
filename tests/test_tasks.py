"""
Tests for task endpoints.
"""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient


class TestCreateTask:
    """Test task creation."""

    def test_create_task_success(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful task creation."""
        response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Complete project",
                "description": "Finish the API development",
                "status": "TODO",
                "priority": "HIGH",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete project"
        assert data["status"] == "TODO"
        assert data["priority"] == "HIGH"
        assert "id" in data

    def test_create_task_with_category(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test creating task with category."""
        # Create category first
        cat_response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"},
        )
        category_id = cat_response.json()["id"]

        # Create task
        response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Work task",
                "category_id": category_id,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["category_id"] == category_id

    def test_create_task_invalid_category(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test creating task with non-existent category."""
        fake_id = str(uuid.uuid4())

        response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Task",
                "category_id": fake_id,
            },
        )

        assert response.status_code == 404

    def test_create_task_no_auth(
        self,
        client: TestClient,
    ):
        """Test creating task without authentication."""
        response = client.post(
            "/api/v1/tasks/",
            json={"title": "Task"},
        )

        assert response.status_code == 401


class TestGetTasks:
    """Test getting tasks."""

    def test_get_my_tasks(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test getting user's tasks."""
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 1"},
        )
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 2"},
        )

        response = client.get("/api/v1/tasks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_get_tasks_with_status_filter(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test filtering tasks by status."""
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 1", "status": "TODO"},
        )
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 2", "status": "COMPLETED"},
        )

        response = client.get(
            "/api/v1/tasks/?status=TODO",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "TODO"

    def test_get_tasks_with_search(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test searching tasks."""
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Complete API",
                "description": "Finish development",
            },
        )
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Write tests",
                "description": "Unit testing",
            },
        )

        response = client.get(
            "/api/v1/tasks/?search=API",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "API" in data["items"][0]["title"]

    def test_get_tasks_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test task pagination."""
        for i in range(15):
            client.post(
                "/api/v1/tasks/",
                headers=auth_headers,
                json={"title": f"Task {i + 1}"},
            )

        response = client.get(
            "/api/v1/tasks/?skip=0&limit=10",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["total_pages"] == 2

    def test_get_task_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test getting specific task."""
        create_response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "My Task"},
        )
        task_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "My Task"


class TestUpdateTask:
    """Test task updates."""

    def test_update_task_success(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful task update."""
        create_response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Old Title", "status": "TODO"},
        )
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
            json={"title": "New Title", "status": "IN_PROGRESS"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["status"] == "IN_PROGRESS"

    def test_update_task_status_only(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test updating only task status."""
        create_response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task", "status": "TODO"},
        )
        task_id = create_response.json()["id"]

        response = client.patch(
            f"/api/v1/tasks/{task_id}/status?new_status=COMPLETED",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_update_task_priority_only(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test updating only task priority."""
        create_response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task", "priority": "LOW"},
        )
        task_id = create_response.json()["id"]

        response = client.patch(
            f"/api/v1/tasks/{task_id}/priority?new_priority=URGENT",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "URGENT"


class TestDeleteTask:
    """Test task deletion."""

    def test_delete_task_success(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful task deletion."""
        create_response = client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task to delete"},
        )
        task_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        get_response = client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404


class TestTaskStatistics:
    """Test task statistics endpoint."""

    def test_get_statistics(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test getting task statistics."""
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 1", "status": "TODO"},
        )
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 2", "status": "TODO"},
        )
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={"title": "Task 3", "status": "COMPLETED"},
        )

        response = client.get(
            "/api/v1/tasks/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["by_status"]["todo"] == 2
        assert data["by_status"]["completed"] == 1


class TestOverdueTasks:
    """Test overdue tasks endpoint."""

    def test_get_overdue_tasks(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test getting overdue tasks."""
        past_date = (datetime.utcnow() - timedelta(days=2)).isoformat()
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Overdue Task",
                "status": "TODO",
                "due_date": past_date,
            },
        )

        future_date = (datetime.utcnow() + timedelta(days=2)).isoformat()
        client.post(
            "/api/v1/tasks/",
            headers=auth_headers,
            json={
                "title": "Future Task",
                "status": "TODO",
                "due_date": future_date,
            },
        )

        response = client.get(
            "/api/v1/tasks/overdue",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Overdue Task"
        assert data[0]["is_overdue"] is True
