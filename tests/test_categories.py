"""
Tests for category endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class TestCreateCategory:
    """Test category creation."""
    
    def test_create_category_success(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test successful category creation."""
        response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={
                "name": "Work",
                "color": "#FF5733"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Work"
        assert data["color"] == "#FF5733"
        assert "id" in data
    
    def test_create_category_duplicate_name(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test creating category with duplicate name."""
        # Create first category
        client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        
        # Try to create duplicate
        response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#0000FF"}
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_create_category_invalid_color(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test creating category with invalid color format."""
        response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={
                "name": "Work",
                "color": "invalid"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_category_no_auth(self, client: TestClient):
        """Test creating category without authentication."""
        response = client.post(
            "/api/v1/categories/",
            json={"name": "Work", "color": "#FF5733"}
        )
        
        assert response.status_code == 401


class TestGetCategories:
    """Test getting categories."""
    
    def test_get_my_categories(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting user's categories."""
        # Create some categories
        client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Personal", "color": "#00FF00"}
        )
        
        # Get categories
        response = client.get("/api/v1/categories/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(cat["name"] == "Work" for cat in data)
        assert any(cat["name"] == "Personal" for cat in data)
    
    def test_get_category_by_id(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting specific category."""
        # Create category
        create_response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        category_id = create_response.json()["id"]
        
        # Get category
        response = client.get(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == "Work"
    
    def test_get_category_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting non-existent category."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = client.get(
            f"/api/v1/categories/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestUpdateCategory:
    """Test category updates."""
    
    def test_update_category_success(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test successful category update."""
        # Create category
        create_response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        category_id = create_response.json()["id"]
        
        # Update category
        response = client.put(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers,
            json={"name": "Business", "color": "#0000FF"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Business"
        assert data["color"] == "#0000FF"
    
    def test_update_category_partial(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test partial category update."""
        # Create category
        create_response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        category_id = create_response.json()["id"]
        
        # Update only name
        response = client.put(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers,
            json={"name": "Business"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Business"
        assert data["color"] == "#FF5733"  # Unchanged


class TestDeleteCategory:
    """Test category deletion."""
    
    def test_delete_category_success(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test successful category deletion."""
        # Create category
        create_response = client.post(
            "/api/v1/categories/",
            headers=auth_headers,
            json={"name": "Work", "color": "#FF5733"}
        )
        category_id = create_response.json()["id"]
        
        # Delete category
        response = client.delete(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/categories/{category_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404