
"""
Tests for error handling and custom exceptions.
"""

import pytest
from fastapi.testclient import TestClient


class TestErrorResponses:
    """Test error response formats."""
    
    def test_validation_error_format(self, client: TestClient):
        """Test validation errors have correct format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",  # Invalid email
                "username": "ab",  # Too short
                "password": "short"  # Too short
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        assert "errors" in data
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) > 0
    
    def test_authentication_error_format(self, client: TestClient):
        """Test authentication errors have correct format."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data
    
    def test_not_found_error_format(self, client: TestClient, auth_headers):
        """Test not found errors have correct format."""
        import uuid
        fake_id = uuid.uuid4()
        
        response = client.get(
            f"/api/v1/tasks/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing protected endpoint without auth."""
        response = client.get("/api/v1/tasks/")
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data