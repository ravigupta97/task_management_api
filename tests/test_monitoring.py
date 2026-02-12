
"""
Tests for monitoring and metrics functionality.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check_success(self, client: TestClient):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["healthy", "degraded"]
        assert data["app_name"] == "Task Management API"
        assert "version" in data
        assert "environment" in data
        assert "database" in data
    
    def test_health_check_database_status(self, client: TestClient):
        """Test that health check includes database status."""
        response = client.get("/health")
        
        data = response.json()
        assert data["database"] == "healthy"


class TestMetrics:
    """Test metrics endpoint."""
    
    def test_metrics_endpoint(self, client: TestClient):
        """Test metrics endpoint returns data."""
        # Make some requests first
        client.get("/health")
        client.get("/")
        
        # Get metrics
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "uptime" in data
        assert "total_requests" in data
        assert "total_errors" in data
        assert "slowest_endpoints" in data
        assert data["total_requests"] > 0
    
    def test_metrics_reset(self, client: TestClient):
        """Test metrics can be reset."""
        # Make some requests
        client.get("/health")
        
        # Check metrics exist
        response = client.get("/metrics")
        data = response.json()
        requests_before = data["total_requests"]
        assert requests_before > 0
        
        # Reset metrics
        reset_response = client.post("/metrics/reset")
        assert reset_response.status_code == 200
        
        # Verify metrics were reset
        response = client.get("/metrics")
        data = response.json()
        # Note: will include the GET /metrics request itself
        assert data["total_requests"] < requests_before