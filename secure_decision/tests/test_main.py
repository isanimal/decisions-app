import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)

class TestMainApp:
    """Test cases for main FastAPI app"""

    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_password_hashing(self):
        """Test password hashing functions"""
        from app.main import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_normalize_status(self):
        """Test status normalization"""
        from app.main import normalize_status

        assert normalize_status("draft") == "DRAFT"
        assert normalize_status("ACTIVE") == "ACTIVE"
        assert normalize_status("invalid") == "DRAFT"
        assert normalize_status(None) == "DRAFT"